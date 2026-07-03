# import random
# import dramatiq
# import redis
# from typing import cast
# from sqlalchemy.orm import sessionmaker
#
# from src.core.config.settings import config
# from src.shared.infrastructure.db import sync_engine
# from src.shared.infrastructure.logger import logger
# from src.shared.infrastructure.outbox.outbox_worker import OutboxWorker
# from dramatiq.brokers.redis import RedisBroker
#
# SyncSession = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)
# dramatiq.set_broker(RedisBroker(url=config.REDIS_URL))
# OUTBOX_POLLER_RUN_LOCK_KEY = "outbox:poller:run:lock"
# OUTBOX_POLLER_RUN_LOCK_TTL_SECONDS = 30
#
#
# @dramatiq.actor(queue_name="outbox")
# def process_outbox():
#     """
#     polling the outbox table for pending messages and processing them, this task will run in a separate thread or process and continuously poll the outbox table for new events to process.
#     """
#     redis_client = redis.Redis.from_url(config.REDIS_URL, decode_responses=True)
#     lock_acquired = redis_client.set(
#         OUTBOX_POLLER_RUN_LOCK_KEY,
#         "1",
#         nx=True,
#         ex=OUTBOX_POLLER_RUN_LOCK_TTL_SECONDS,
#     )
#     if not lock_acquired:
#         logger.info("[Outbox] Poller run skipped because another poller is active.")
#         redis_client.close()
#         return
#
#     session = SyncSession()
#     try:
#         worker = OutboxWorker(session)
#         worker.process()
#     except Exception as e:
#         logger.error(f"[Outbox] Polling run failed: {e}")
#     finally:
#         session.close()
#         redis_client.delete(OUTBOX_POLLER_RUN_LOCK_KEY)
#         redis_client.close()
#         if config.OUTBOX_POLLER_AUTOSTART:
#             delay_seconds = random.randint(
#                 config.OUTBOX_POLLER_DELAY_INITIAL_SECONDS,
#                 config.OUTBOX_POLLER_DELAY_MAX_SECONDS,
#             )
#             logger.info(f"[Outbox] Scheduling next poll in {delay_seconds}s")
#             process_outbox.send_with_options(delay=delay_seconds)
#
#
# process_outbox = cast(dramatiq.Actor, process_outbox)
