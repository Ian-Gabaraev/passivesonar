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


def gather_system_metrics():
    return f"""
🌡️CPU Temperature: {get_cpu_temperature()},
🔋Battery: {get_battery()},
📊CPU Usage: {get_cpu_usage()}%,
💾RAM Usage: {get_ram_usage()}%,
⏱️System Uptime: {get_system_uptime()},
"""


def log_system_metrics():
    system_metrics = gather_system_metrics()
    push_system_metrics_to_redis(system_metrics)
    time.sleep(5)


if __name__ == "__main__":
    while True:
        log_system_metrics()
