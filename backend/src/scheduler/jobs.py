import asyncio
import logging
import time
from src.alerts.service import AlertService
from src.database import AsyncSessionLocal
from src.metrics.service import MetricService
from src.scheduler.config import scheduler_config

logger = logging.getLogger(__name__)


async def run_evaluation_job():
    async with AsyncSessionLocal() as db:
        try:
            await AlertService.evaluate_all_rules(db)
        except Exception as e:
            logger.error(f"Error during alert rule evaluation job: {e}")


async def run_offline_sweep_job():
    async with AsyncSessionLocal() as db:
        try:
            count = await AlertService.check_offline_servers(
                db,
                timeout_seconds=scheduler_config.OFFLINE_TIMEOUT_SECONDS
            )
            if count > 0:
                logger.info(f"Offline sweep flagged {count} server(s) as offline.")
        except Exception as e:
            logger.error(f"Error during offline server sweep job: {e}")


async def run_metric_cleanup_job():
    async with AsyncSessionLocal() as db:
        try:
            count = await MetricService.delete_old_metrics(
                db,
                retention_days=scheduler_config.METRICS_RETENTION_DAYS
            )
            if count > 0:
                logger.info(f"Data retention cleanup deleted {count} metric row(s) older than {scheduler_config.METRICS_RETENTION_DAYS} days.")
        except Exception as e:
            logger.error(f"Error during metric cleanup job: {e}")


async def scheduler_loop():
    logger.info("Starting SMP Scheduler Loop...")
    last_cleanup_time = 0.0
    while True:
        try:
            await run_evaluation_job()
            await run_offline_sweep_job()

            now = time.monotonic()
            if now - last_cleanup_time >= scheduler_config.METRICS_CLEANUP_INTERVAL_SECONDS:
                await run_metric_cleanup_job()
                last_cleanup_time = now
        except Exception as e:
            logger.error(f"Error in scheduler loop tick: {e}")

        await asyncio.sleep(scheduler_config.ALERT_EVALUATION_INTERVAL_SECONDS)

