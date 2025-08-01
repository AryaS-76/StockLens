from apscheduler.schedulers.background import BackgroundScheduler
from backend.stock_loader import fetch_and_store_stock_data

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store_stock_data, 'interval', minutes=5)
    scheduler.start()
    print("✅ Scheduler started and job scheduled every 5 minutes.")

