import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from pigenus.scheduler.tasks import (
    rotate_logs,
    create_backup,
    summarize_sessions,
    requeue_stuck_jobs,
    mark_offline_workers,
    prepare_daily_briefing,
)

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def run_nightly_maintenance():
    rotate_logs()
    create_backup()
    summarize_sessions()
    prepare_daily_briefing()


def setup_scheduler():
    scheduler.add_job(run_nightly_maintenance, CronTrigger(hour=2, minute=0),
                      id="nightly_maintenance", replace_existing=True)
    scheduler.add_job(mark_offline_workers, IntervalTrigger(minutes=5),
                      id="mark_offline_workers", replace_existing=True)
    scheduler.add_job(requeue_stuck_jobs, IntervalTrigger(minutes=15),
                      id="requeue_stuck_jobs", replace_existing=True)
    logger.info("Scheduler jobs configured.")


def start_scheduler():
    setup_scheduler()
    scheduler.start()
    logger.info("Scheduler started.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
