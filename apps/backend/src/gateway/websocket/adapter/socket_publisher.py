from src.gateway.websocket.inteface.realtime_publisher import IRealTimePublisher


class SocketIORealTimePublisher(IRealTimePublisher):
    """
    Adapter implementing the real-time publisher using python-socketio.
    """

    async def emit(
        self, event: str, data: dict, room: str, namespace: str = "/"
    ) -> None:
        from src.gateway.websocket.socket_manager import sio

        await sio.emit(event=event, data=data, room=room, namespace=namespace)
