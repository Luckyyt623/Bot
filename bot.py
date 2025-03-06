import os
import requests
import yt_dlp
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Replace with your bot token and song recognition API key
BOT_TOKEN = "8127744294:AAHJjwnzxzQ8uDN6__iRFke8FmJLSEDjNaw"
SONG_API_KEY = "YOUR_SONG_RECOGNITION_API_KEY"
SONG_API_URL = "https://api.audd.io/"  # Example API, modify based on your service

def download_video(video_url):
    """Downloads the video and extracts audio."""
    output_path = "video.mp4"
    ydl_opts = {"outtmpl": output_path, "format": "bestaudio"}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    
    return output_path

def recognize_song(audio_path):
    """Sends audio to API and gets song details."""
    with open(audio_path, "rb") as audio_file:
        files = {"file": audio_file}
        data = {"api_token": SONG_API_KEY}
        response = requests.post(SONG_API_URL, data=data, files=files)
    
    return response.json()

def handle_message(update: Update, context: CallbackContext):
    """Handles incoming messages with video links."""
    video_url = update.message.text
    update.message.reply_text("Downloading video...")

    try:
        video_path = download_video(video_url)
        song_info = recognize_song(video_path)

        if "result" in song_info:
            title = song_info["result"]["title"]
            artist = song_info["result"]["artist"]
            update.message.reply_text(f"🎵 Song Found: {title} by {artist}")
        else:
            update.message.reply_text("Sorry, couldn't recognize the song.")

    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")

def start(update: Update, context: CallbackContext):
    """Sends welcome message."""
    update.message.reply_text("Send me a video link, and I'll find the song for you!")

def main():
    """Main function to start the bot."""
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()