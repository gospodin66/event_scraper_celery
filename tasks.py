from celery import Celery
from pathlib import Path
import subprocess
import sys
import re
from datetime import datetime

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
        
        output = output.split('\n\n', 1)[1] if '\n\n' in output else output
        events = []
        venues = [section for section in output.split('\n\n') if ':' in section and 'Script' not in section]
        for venue in venues:
            venue_name, *event_lines = venue.split(':\n')
            for event_line in '\n'.join(event_lines).split('\n'):
                if event_line.strip():
                    regex = re.compile(r'(.*?) :: (https:\/\/www\.facebook\.com\/events\/\d+\/)')
                    match = regex.match(event_line)
                    if match:
                        event_info = match.group(1).strip()
                        link = match.group(2)
                        date_pattern = re.compile(r'(\w{3}, \w{3} \d{1,2} at \d{1,2}:\d{2}\u202f\w{2} \w{3})')
                        date_match = date_pattern.search(event_info)
                        if date_match:
                            when_str = date_match.group(1)
                            when = datetime.strptime(when_str, '%a, %b %d at %I:%M\u202f%p %Z')
                            event_info = event_info.replace(when_str, '').strip()
                        else:
                            when = datetime.now()
                        events.append({
                            'venue': venue_name.strip(),
                            'name': event_info,
                            'link': link,
                            'when': when.isoformat()
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
