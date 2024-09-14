from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from .utils import computeDailyStock
from .utils import send_wechat

logger = logging.getLogger(__name__)

def computeDailyStockAndSendMsg(**kwargs):
    msg = computeDailyStock()
    send_wechat(msg)
    logger.debug(f"定时任务执行了:{kwargs.get('执行时间', datetime.now())}")

def __initSchedule__():
    scheduler = BackgroundScheduler()
    scheduler.add_job(computeDailyStockAndSendMsg, 'cron', **{"start_date": "2024-09-12 10:38:00", "end_date": "2029-06-18 10:38:20", "hours": "8/24"})
    logger.debug("定时任务开始")
    scheduler.start()

__initSchedule__()