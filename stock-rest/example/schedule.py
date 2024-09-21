from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from .utils import computeDailyStock
from .utils import send_wechat

logger = logging.getLogger(__name__)

def computeDailyStockAndSendMsg(**kwargs):
    logger.debug(f"定时任务准备执行:{kwargs.get('执行时间', datetime.now())}")
    msg = computeDailyStock()
    send_wechat(msg)
    logger.debug(f"定时任务执行了:{kwargs.get('执行时间', datetime.now())}")

def __initSchedule__():
    scheduler = BackgroundScheduler()
    scheduler.add_job(computeDailyStockAndSendMsg, 'cron', **{"hour": "8"})
    logger.debug("定时任务开始")
    scheduler.start()

__initSchedule__()