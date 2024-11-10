from celery import Celery
from pathlib import Path
import subprocess
import sys

# Initialize Celery with RabbitMQ
celery = Celery('tasks',
                broker='amqp://guest:guest@localhost:5672//',
                backend='rpc://')

# Load additional configurations
celery.config_from_object('event_scraper_celery.celeryconfig')

@celery.task(bind=True)
def run_scraper_task(self):
    try:
        # Get path to scraper script
        script_path = Path(__file__).parent.parent / 'event_scraper' / 'src' / 'init.py'
        
        if not script_path.exists():
            raise FileNotFoundError(f"Scraper script not found at: {script_path}")

        # Run the scraper script
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Get output and errors
        output, error = process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Scraper failed with error: {error}")
            
        return {
            'status': 'SUCCESS',
            'output': output,
            'error': error if error else None
        }
        
    except Exception as e:
        return {
            'status': 'ERROR',
            'error': str(e)
        }