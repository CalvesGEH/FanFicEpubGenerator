from apscheduler.schedulers.blocking import BlockingScheduler
import datetime
import os

from common import get_config, get_logger
from scheduler import RoyalRoadScheduler

config = get_config()
log = get_logger(__name__)


def directory_check():
    log.info(f'Running check for directories and permissions...')
    log.debug(f'Running directory check for user: euid: {os.geteuid()}')
    # Ensure that config.INGEST_DIR exists and is writable
    if not os.path.exists(config.INGEST_DIR):
        os.makedirs(config.INGEST_DIR)
    if not os.access(config.INGEST_DIR, os.W_OK):
        log.error(f"INGEST_DIR {config.INGEST_DIR} is not writable! Please make sure that the current user has write permissions to this directory and it exists.")
        exit(1)
    if config.ROYAL_ROAD_DOWNLOAD_FILE:
        if not os.access(config.ROYAL_ROAD_DOWNLOAD_FILE, os.R_OK):
            log.error(f"ROYAL_ROAD_DOWNLOAD_FILE {config.ROYAL_ROAD_DOWNLOAD_FILE} does not exist or is unreadable!")
            exit(1)
    log.info(f'Directory check complete.')


def networking_check():
    log.info(f'Running check for networking...')
    # Check for internet connection
    import requests
    try:
        requests.get('https://www.google.com')
    except requests.exceptions.RequestException as e:
        log.error(f'Could not connect to the internet. Please check your network connection.')
        exit(1)
    log.info(f'Networking check complete.')


if __name__ == '__main__':

    log.debug(f'FanFicEpubGenerator starting up with config: {config}')

    log.info(f'Setting up FanFicEpubGenerator and running checks...')
    
    # System checks
    directory_check()
    networking_check()

    log.info(f'FanFicEpubGenerator checks complete.')

    log.info(f'Creating scheduler for jobs...')
    scheduler = BlockingScheduler()

    # Setting up RoyalRoad scheduler
    log.info(f'Creating RoyalRoadScheduler...')
    royal_road_scheduler = RoyalRoadScheduler()
    scheduler.add_job(royal_road_scheduler.run, 'interval', minutes=config.UPDATE_INTERVAL_MINUTES)

    log.info(f'Schedulers created. Starting scheduler...')
    try:
        for job in scheduler.get_jobs():
            log.debug(f'Editing {job.name} to run immediately...')
            job.modify(next_run_time=datetime.datetime.now())
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info(f'Stopping scheduler...')
        scheduler.shutdown()
        log.info(f'Scheduler stopped.')
        exit(0)

