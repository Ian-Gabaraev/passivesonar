#!/bin/bash

# Launch celery worker
celery -A celeryapps worker --loglevel=info &
python3 constant_noise.py &
python3 screen.py &
wait
