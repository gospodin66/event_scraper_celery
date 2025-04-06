from celery import Celery
from pathlib import Path
import subprocess
import sys

app = Celery('tasks')
app.config_from_object('event_scraper_celery.celeryconfig')

@app.task(bind=True)
def run_scraper_task(self):
    try:
        script_path = Path(__file__).parent.parent / 'event_scraper' / 'src' / 'init.py'

        if not script_path.exists():
            raise FileNotFoundError(f"Scraper script not found at: {script_path}")

        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output, error = process.communicate()

        if process.returncode != 0:
            raise Exception(f"Scraper failed with error: {error}")
        
        events = []
        venues = [section for section in output.split('\n\n') if ':' in section and 'Script' not in section]
        for venue in venues:           
            venue_name, *event_lines = venue.split(':\n')

            for event in event_lines:

                for evt in event.split('\n'):

                    e = evt.split(' :: ')

                    events.append({
                        'venue': venue_name,
                        'name': e[0],
                        'where': e[1],
                        'when': e[2],
                        'link': e[3],
                    })
            
        return {
            'status': 'SUCCESS',
            'events': events,
            'error': error if error else None
        }
        
    except Exception as e:
        return {
            'status': 'ERROR',
            'error': str(e)
        }
