import schedule
import time
from datetime import datetime

def start_scheduler(job_func, interval_days=2, run_time="10:00"):
    schedule.every(interval_days).days.at(run_time).do(job_func)
    print(f"Scheduler started: running every {interval_days} days at {run_time}")
    while True:
        schedule.run_pending()
        time.sleep(60)
