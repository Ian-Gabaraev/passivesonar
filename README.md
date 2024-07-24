## This is a passive sonar emulation in Python
## Requires an array of microphones (at least 4) set up in the same fashion as on submarine to get the most coverage

## How to launch
- ``celery -A celeryapps worker --loglevel=info``
- ``celery -A celeryapps flower --port=5909``
- ``python3 screen.py``
- ``python3 listen.py``
