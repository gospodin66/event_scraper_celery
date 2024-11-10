# Broker settings
broker_url = 'amqp://guest:guest@localhost:5672//'
result_backend = 'rpc://'

broker_connection_retry_on_startup = True

# Task settings
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = True

# Task execution settings
task_track_started = True
task_time_limit = 300  # 5 minutes
task_soft_time_limit = 240  # 4 minutes

# Worker settings
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 50

# Queue settings
task_default_queue = 'scraper_tasks'
task_queues = {
    'scraper_tasks': {
        'binding_key': 'scraper.#'
    }
}