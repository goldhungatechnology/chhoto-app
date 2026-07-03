import asyncio
import uuid

from src.gateway.ws.backplane.interface import IBackplane
from src.gateway.ws.connection import Connection


class ConnectionManager:
    """
    Manages WebSocket connections for users. It maintains a registry of active connections, allowing for efficient retrieval and management of connections based on user IDs. The ConnectionManager supports adding and removing connections, sending messages to specific users or broadcasting to all users, and disconnecting users or all connections. It also integrates with a backplane to enable communication across multiple instances of the gateway, ensuring that messages sent to a user are delivered to all their active connections regardless of which instance they are connected to.
    """

    def __init__(self):
        self._connections: dict[int, dict[str, Connection]] = {}
        # org_id -> set of LOCAL user ids subscribed to that org's presence feed.
        # Membership is per-instance; cross-instance fan-out happens over the
        # backplane (every instance delivers to its own local subscribers).
        self._org_members: dict[int, set[int]] = {}
        self._backplane: IBackplane | None = None
        self._instance_id = uuid.uuid4().hex[:8]
        self._subscriber_task: asyncio.Task | None = None

    # --- Lifecycle ---

    async def start(self, backplane: IBackplane | None = None) -> None:
        """
        Start the ConnectionManager and optionally initialize the backplane for inter-instance communication. If a backplane is provided, it starts a background task to listen for messages from the backplane and route them to the appropriate user connections. This allows the ConnectionManager to receive messages published by other instances of the gateway and deliver them to the correct users, ensuring that messages are properly routed in a distributed environment.
        """
        self._backplane = backplane
        if self._backplane:
            self._subscriber_task = asyncio.create_task(self._backplane_loop())

    async def stop(self) -> None:
        """
        Stop the ConnectionManager and clean up resources. This method disconnects all active connections, cancels the backplane subscriber task if it exists, and closes the backplane connection if it was initialized. It ensures that all resources are properly released when the gateway is shutting down, preventing potential memory leaks or dangling connections.
        """
        await self.disconnect_all()
        if self._subscriber_task:
            self._subscriber_task.cancel()
            try:
                await self._subscriber_task
            except asyncio.CancelledError:
                pass
        if self._backplane:
            await self._backplane.close()
            self._backplane = None

    async def _backplane_loop(self) -> None:
        """
        Background task that listens for messages from the backplane and routes them to the appropriate user connections. It subscribes to channels matching the pattern "ws:user:*" and, upon receiving a message, extracts the user ID from the channel name and sends the message to all active connections for that user. This loop runs indefinitely until the ConnectionManager is stopped, allowing it to continuously receive and route messages from other instances of the gateway.
        """
        assert self._backplane is not None
        async for channel, message in self._backplane.subscribe(
            ["ws:user:*", "ws:org:*"]
        ):
            if channel.startswith("ws:user:"):
                user_id = int(channel.rsplit(":", 1)[-1])
                for conn in self.get_user_connections(user_id):
                    await conn.send_json(message)
            elif channel.startswith("ws:org:"):
                organization_id = int(channel.rsplit(":", 1)[-1])
                await self._deliver_to_org_members(organization_id, message)

    # --- Registry ---

    def add_connection(self, user_id: int, connection: Connection) -> None:
        """
        Add a new connection for a user. The connection is stored in a nested dictionary where the outer key is the user ID and the inner key is the connection ID. This allows for efficient retrieval of connections based on user IDs and supports multiple connections per user. When a new connection is added, it is registered under the corresponding user ID, enabling the ConnectionManager to manage and route messages to all active connections for that user.
        """
        self._connections.setdefault(user_id, {})[connection.connection_id] = connection

    def remove_connection(self, user_id: int, connection_id: str) -> None:
        """
        Remove a connection for a user. The method looks up the connection by user ID and connection ID, removes it from the registry, and if the user has no more active connections, it removes the user entry from the registry. This ensures that the ConnectionManager maintains an accurate record of active connections and can efficiently manage resources by cleaning up entries for users who are no longer connected.
        """
        conns = self._connections.get(user_id)
        if conns:
            conns.pop(connection_id, None)
            if not conns:
                del self._connections[user_id]
                # Last connection for this user is gone — drop its org
                # presence subscriptions so we don't leak into _org_members.
                self._purge_user_org_subscriptions(user_id)

    def get_connection(self, user_id: int, connection_id: str) -> Connection | None:
        """
        Retrieve a specific connection for a user based on the user ID and connection ID. The method looks up the connection in the nested dictionary and returns it if found, or None if the connection does not exist. This allows for efficient retrieval of individual connections, enabling the ConnectionManager to manage and route messages to specific connections when necessary.
        """
        return self._connections.get(user_id, {}).get(connection_id)

    def get_user_connections(self, user_id: int) -> list[Connection]:
        """
        Retrieve all active connections for a specific user based on the user ID. The method returns a list of Connection objects for the user, or an empty list if the user has no active connections. This allows the ConnectionManager to manage and route messages to all active connections for a user, ensuring that messages are delivered to all devices or sessions associated with that user.
        """
        return list(self._connections.get(user_id, {}).values())

    # --- Push API ---

    async def send_to_user(self, user_id: int, message: dict) -> None:
        """
        Send a message to all active connections for a specific user. The method retrieves all connections for the user and sends the message to each connection. If a backplane is initialized, it also publishes the message to the backplane channel for that user, allowing other instances of the gateway to receive and route the message to their active connections for that user. This ensures that messages sent to a user are delivered to all their active connections regardless of which instance they are connected to.
        """
        for conn in self.get_user_connections(user_id):
            await conn.send_json(message)
        if self._backplane:
            await self._backplane.publish(f"ws:user:{user_id}", message)

    # --- Org presence rooms ---

    def subscribe_to_org(self, organization_id: int, user_id: int) -> None:
        """
        Subscribe a (local) user to an organization's presence feed. Used by
        agents who want live visitor updates for an organization they belong to.
        """
        self._org_members.setdefault(organization_id, set()).add(user_id)

    def unsubscribe_from_org(self, organization_id: int, user_id: int) -> None:
        """Remove a user from an organization's presence feed."""
        members = self._org_members.get(organization_id)
        if members:
            members.discard(user_id)
            if not members:
                del self._org_members[organization_id]

    def _purge_user_org_subscriptions(self, user_id: int) -> None:
        """Drop a user from every org room (called when they fully disconnect)."""
        for organization_id in list(self._org_members):
            self.unsubscribe_from_org(organization_id, user_id)

    async def _deliver_to_org_members(
        self, organization_id: int, message: dict
    ) -> None:
        """Send a message to every local connection subscribed to an org room."""
        for user_id in list(self._org_members.get(organization_id, set())):
            for conn in self.get_user_connections(user_id):
                await conn.send_json(message)

    async def publish_to_org(self, organization_id: int, message: dict) -> None:
        """
        Deliver a message to every agent subscribed to an organization's presence
        feed, across all gateway instances. Delivers locally and publishes to the
        backplane so peer instances reach their own local subscribers. The
        backplane filters out the publisher's own message, so there is no
        double-delivery.
        """
        await self._deliver_to_org_members(organization_id, message)
        if self._backplane:
            await self._backplane.publish(f"ws:org:{organization_id}", message)

    async def broadcast(self, message: dict) -> None:
        """
        Broadcast a message to all active connections for all users. The method iterates through all connections in the registry and sends the message to each connection. This allows the ConnectionManager to efficiently broadcast messages to all connected clients, which can be useful for system-wide notifications or updates that need to be delivered to every user regardless of their individual connections.
        """
        for conns in self._connections.values():
            for conn in conns.values():
                await conn.send_json(message)

    async def disconnect_user(self, user_id: int) -> None:
        """
        Disconnect all active connections for a specific user. The method retrieves all connections for the user, closes each connection, and removes the user entry from the registry. This allows the ConnectionManager to efficiently disconnect a user from all their active sessions, which can be useful for enforcing account security or handling user-initiated logouts.
        """
        for conn in self.get_user_connections(user_id):
            await conn.close()
        self._connections.pop(user_id, None)

    async def disconnect_all(self) -> None:
        """
        Disconnect all active connections for all users. The method iterates through all user entries in the registry, closes each connection, and clears the registry. This allows the ConnectionManager to efficiently disconnect all users, which can be useful during system shutdowns or maintenance periods to ensure that all connections are properly closed and resources are released.
        """
        for user_id in list(self._connections):
            await self.disconnect_user(user_id)

    # --- Observability ---

    @property
    def online_user_ids(self) -> set[int]:
        """
        Get a set of user IDs that currently have active connections. The method returns a set of user IDs based on the keys of the connections registry, allowing for efficient retrieval of all users who are currently online and have at least one active connection.
        """
        return set(self._connections.keys())

    @property
    def total_connections(self) -> int:
        """
        Get the total number of active connections across all users. The method calculates the total by summing the lengths of the connection dictionaries for each user, providing an aggregate count of all active WebSocket connections managed by the ConnectionManager.
        """
        return sum(len(c) for c in self._connections.values())


connection_manager = ConnectionManager()
