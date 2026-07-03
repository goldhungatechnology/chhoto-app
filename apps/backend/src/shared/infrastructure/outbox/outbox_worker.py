# import asyncio
# import inspect
# import json
# from typing import Any
# from datetime import UTC, datetime
# from src.shared.infrastructure.logger import logger
# from src.shared.infrastructure.outbox.outbox_registry import handlers
# from src.shared.infrastructure.outbox.outbox_models import OutboxModel
# from sqlalchemy import text
#
#
# class OutboxWorker:
#     """
#     the outbox worker is responsible for processing events from the outbox table, it will run in a separate thread or process and continuously poll the outbox table for new events to process.
#     """
#
#     def __init__(self, session):
#         self.session = session
#
#     @staticmethod
#     def _execute_handler(handler, payload: dict) -> None:
#         result = handler(payload)
#         if inspect.isawaitable(result):
#             asyncio.run(result)
#
#     @staticmethod
#     def _decode_payload(raw_payload: Any) -> dict:
#         if isinstance(raw_payload, dict):
#             return raw_payload
#         if isinstance(raw_payload, (str, bytes, bytearray)):
#             decoded = json.loads(raw_payload)
#             if isinstance(decoded, dict):
#                 return decoded
#             raise ValueError("Decoded payload must be a JSON object")
#         raise ValueError(
#             f"Outbox payload must be dict or JSON string, got {type(raw_payload).__name__}"
#         )
#
#     def _claim_events(self, batch_size: int = 100) -> list[OutboxModel]:
#         now = datetime.now(UTC)
#         claim_sql = text(
#             f"""
#             WITH claimed AS (
#                 SELECT id
#                 FROM {OutboxModel.__tablename__}
#                 WHERE processed = false
#                   AND locked_at IS NULL
#                 ORDER BY id
#                 FOR UPDATE SKIP LOCKED
#                 LIMIT :batch_size
#             )
#             UPDATE {OutboxModel.__tablename__} outbox
#             SET locked_at = :locked_at
#             FROM claimed
#             WHERE outbox.id = claimed.id
#             RETURNING outbox.id
#             """
#         )
#         rows = self.session.execute(
#             claim_sql,
#             {"batch_size": batch_size, "locked_at": now},
#         ).all()
#         if not rows:
#             return []
#
#         claimed_ids = [row[0] for row in rows]
#         events = (
#             self.session.query(OutboxModel)
#             .filter(OutboxModel.id.in_(claimed_ids))
#             .order_by(OutboxModel.id.asc())
#             .all()
#         )
#         self.session.commit()
#         return events
#
#     def process(self):
#         """
#         Process outbox events safely with locking.
#         """
#         events = self._claim_events(batch_size=100)
#
#         for event in events:
#             handler = handlers.get(event.event_type)
#
#             if not handler:
#                 logger.warning(
#                     f"[Outbox] No handler for event type: {event.event_type}"
#                 )
#                 event.locked_at = None
#                 event.last_error = f"No handler for event type: {event.event_type}"
#                 event.retry_count += 1
#                 self.session.commit()
#                 continue
#
#             try:
#                 payload = self._decode_payload(event.payload)
#
#                 self._execute_handler(handler, payload)
#
#                 # 3. mark processed
#                 event.processed = True
#                 event.locked_at = None
#                 event.last_error = None
#
#             except Exception as e:
#                 logger.error(f"[Outbox Failed] Failed {event.event_type}: {e}")
#
#                 # release lock so retry can happen
#                 event.locked_at = None
#                 event.last_error = str(e)
#                 event.retry_count += 1
#
#             self.session.commit()
