import os
import telebot
from dotenv import load_dotenv

load_dotenv()


bot_token = os.getenv("BOT_TOKEN")
main_chat_id = os.getenv("MAIN_CHAT_ID")
bot = telebot.TeleBot(bot_token)


def send_audio_message(audio):
    bot.send_audio(main_chat_id, audio, "Loud noise")
