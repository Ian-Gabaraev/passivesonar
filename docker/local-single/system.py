import os
import time

from telegram.utils import (
    get_cpu_temperature,
    get_battery,
    get_cpu_usage,
    get_ram_usage,
    get_system_uptime,
)

from dotenv import load_dotenv
from utils.redis_q import push_system_metrics_to_redis

load_dotenv()

SYSTEM_Q_NAME = os.getenv("SYSTEM_Q_NAME")


def gather_system_metrics():
    return f"""
"cpu_temperature": {get_cpu_temperature()},
"battery": {get_battery()},
"cpu_usage": {get_cpu_usage()}%",
"ram_usage": {get_ram_usage()}%",
"system_uptime": {get_system_uptime()},
"""


def log_system_metrics():
    system_metrics = gather_system_metrics()
    push_system_metrics_to_redis(system_metrics)
    time.sleep(5)


if __name__ == "__main__":
    while True:
        log_system_metrics()
