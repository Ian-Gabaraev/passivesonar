from celery import Celery
import redis
import json

app = Celery(
    "audio_processor",
    broker="redis://localhost:9812/0",
    backend="redis://localhost:9812/0",
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


r = redis.Redis(host="localhost", port=9812, db=0)


@app.task
def init_screen():
    return "Screen initialized"


@app.task
def kill_screen():
    task = json.dumps("kill")
    r.publish("pygame_commands", task)
    return "Screen killed"


@app.task
def display_device_name(device_name):
    task = json.dumps(("display_device_name", device_name))
    r.publish("pygame_commands", task)
    return f"Device name displayed: {device_name}"


@app.task
def analyze(rms):
    task = json.dumps(("analyze", rms))
    r.publish("pygame_commands", task)
    return "RMS Analysis completed"


@app.task
def draw_circle(color, position, radius):
    task = json.dumps(("draw_circle", (color, position, radius)))
    r.publish("pygame_commands", task)
    return f"Circle drawn at {position} with radius {radius}"


@app.task
def clear_screen():
    task = json.dumps("clear")
    r.publish("pygame_commands", task)
    return "Screen cleared"
