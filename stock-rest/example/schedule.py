from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger(__name__)

def job_function(**kwargs):
    logger.info(kwargs.get("name", "没有传递名称"))
    logger.info(f"定时任务执行了:{kwargs.get('执行时间', datetime.now())}")

def __initSchedule__():
    scheduler = BackgroundScheduler()
    logger.info("定时任务注册开始")
    scheduler.add_job(job_function, 'cron', **{"start_date": "2024-09-12 10:38:00", "end_date": "2029-06-18 10:38:20", "second": "*/2"})
    logger.info("定时任务开始")
    scheduler.start()
