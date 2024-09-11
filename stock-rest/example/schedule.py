from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler


def job_function(**kwargs):
    print(kwargs.get("name", "没有传递名称"))
    print(f"定时任务执行了:{kwargs.get('执行时间', datetime.now())}")


scheduler = BackgroundScheduler()

scheduler.add_job(job_function, 'cron', **{"start_date": "2024-09-12 10:38:00", "end_date": "2029-06-18 10:38:20", "second": "*/2"})


scheduler.start()

while True:
    pass