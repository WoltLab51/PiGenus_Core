def test_scheduler_can_be_imported():
    from pigenus.scheduler import nightly, tasks
    assert hasattr(nightly, "scheduler")
    assert hasattr(nightly, "setup_scheduler")
    assert hasattr(nightly, "start_scheduler")
    assert hasattr(nightly, "stop_scheduler")


def test_scheduler_tasks_importable():
    from pigenus.scheduler.tasks import (
        rotate_logs,
        create_backup,
        summarize_sessions,
        requeue_stuck_jobs,
        mark_offline_workers,
        prepare_daily_briefing,
    )
    assert callable(rotate_logs)
    assert callable(create_backup)
    assert callable(summarize_sessions)


def test_scheduler_instance_exists():
    from pigenus.scheduler.nightly import scheduler
    assert scheduler is not None
