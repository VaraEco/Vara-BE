import os
from dotenv import load_dotenv

load_dotenv()

workers = int(os.environ.get('GUNICORN_PROCESSES', '1'))

threads = int(os.environ.get('GUNICORN_THREADS', '1'))

# timeout = int(os.environ.get('GUNICORN_TIMEOUT', '120'))

forwarded_allow_ips = '*'

secure_scheme_headers = { 'X-Forwarded-Proto': 'https' }