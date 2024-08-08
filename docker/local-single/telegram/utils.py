import datetime

import psutil
import subprocess


def get_cpu_temperature():
    try:
        result = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True)
    except FileNotFoundError:
        return "N/A"

    temp_str = result.stdout.decode()
    temp_value = float(temp_str.split("=")[1].split("'")[0])
    return temp_value


def get_ram_usage():
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total / (1024**2)  # Convert from bytes to MB
    used_memory = memory_info.used / (1024**2)  # Convert from bytes to MB
    free_memory = memory_info.free / (1024**2)  # Convert from bytes to MB

    return total_memory, used_memory, free_memory


def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def get_system_uptime():
    boot_time_timestamp = psutil.boot_time()
    boot_time = datetime.datetime.fromtimestamp(boot_time_timestamp)
    uptime = datetime.datetime.now() - boot_time

    return str(uptime).split(".")[0]


def get_battery():

    return psutil.sensors_battery().percent
