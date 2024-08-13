import json
import os

import redis
import telebot
from dotenv import load_dotenv
from telebot import types

from aws import (
    get_tg_bot_key,
    get_main_chat_id,
    get_batch_size,
    get_listening_duration,
    get_sampling_rate,
    get_chunk_size,
    get_loudness_threshold,
    get_recording_duration,
)

load_dotenv()


bot_token = os.getenv("BOT_TOKEN", get_tg_bot_key())
main_chat_id = os.getenv("MAIN_CHAT_ID", int(get_main_chat_id()))
bot = telebot.TeleBot(bot_token)

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_Q_NAME = os.getenv("REDIS_Q_NAME")
REDIS_AUDIO_Q_NAME = os.getenv("REDIS_AUDIO_Q_NAME")
REDIS_SYSTEM_Q_NAME = os.getenv("REDIS_SYSTEM_Q_NAME")
REDIS_CONTROL_Q_NAME = os.getenv("REDIS_CONTROL_Q_NAME")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=3)
    btn1 = types.KeyboardButton("Reset 🫙Queues")
    btn2 = types.KeyboardButton("Listen 🎙️ Live")
    btn3 = types.KeyboardButton("Stop 🛑 Listening")
    btn4 = types.KeyboardButton("Restart 🔄 Listening")
    btn5 = types.KeyboardButton("System 📊 Stats")
    btn6 = types.KeyboardButton("System ⚙️ Settings")
    markup.add(
        btn1,
        btn2,
        btn3,
        btn4,
        btn5,
        btn6,
    )
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)


def send_plot(plot_file):
    bot.send_photo(main_chat_id, plot_file)


def send_audio_message(audio, message="Loud noise"):
    bot.send_audio(main_chat_id, audio, message)


@bot.message_handler(func=lambda message: message.text == "Stop 🛑 Listening")
def handle_message(message):
    r.rpush(REDIS_CONTROL_Q_NAME, "stop")


@bot.message_handler(func=lambda message: message.text == "Restart 🔄 Listening")
def handle_message(message):
    r.rpush(REDIS_CONTROL_Q_NAME, "start")


@bot.message_handler(func=lambda message: message.text == "Listen 🎙️ Live")
def handle_message(message):
    from celeryapps import record_audio

    record_audio.delay()


@bot.message_handler(func=lambda message: message.text == "System 📊 Stats")
def handle_message(message):
    stats = r.get("system_metrics")
    if stats:
        bot.reply_to(message, json.loads(stats))
    else:
        bot.reply_to(message, "No system stats available")


@bot.message_handler(func=lambda message: message.text == "Reset 🫙Queues")
def handle_message(message):
    r.ltrim(REDIS_Q_NAME, 1, 0)
    r.ltrim(REDIS_AUDIO_Q_NAME, 1, 0)
    r.ltrim(REDIS_CONTROL_Q_NAME, 1, 0)
    bot.reply_to(message, "Queues have been reset")


@bot.message_handler(func=lambda message: message.text == "System ⚙️ Settings")
def handle_message(message):
    settings = f"""
Batch Size: {get_batch_size()}
Listening Duration: {get_listening_duration()} sec
Sampling Rate: {get_sampling_rate()} Hz
Chunk Size: {get_chunk_size()}
Loudness Threshold: {get_loudness_threshold()}
Recording Duration: {get_recording_duration()} sec
"""
    bot.reply_to(message, settings)


if __name__ == "__main__":
    bot.send_message(main_chat_id, "Bot is up and running")
    bot.polling()
