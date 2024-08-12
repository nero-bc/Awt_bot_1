import os
import asyncio
import subprocess
from pyrogram import Client, filters
from flask import Flask
from threading import Thread
from config import Config

# Initialize Flask
flask_app = Flask(__name__)

# Function to trim audio using FFmpeg
async def trim_audio(input_file, output_file, start_time, end_time):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-ss', start_time,
        '-to', end_time,
        '-c:a', 'copy',
        '-y',
        output_file
    ]
    
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        return output_file
    else:
        error_message = stderr.decode()
        print(f"FFmpeg error: {error_message}")
        return None

# /trim_audio command handler
@Client.on_message(filters.command("trim_audio") & filters.reply)
async def trim_audio_handler(client, message):
    if not message.reply_to_message.audio:
        await message.reply("Please reply to an audio file with the command.")
        return

    # Extracting command arguments
    args = message.text.split()
    if len(args) < 3:
        await message.reply("Please provide the start and end times in the format: `/trim_audio start_time end_time`\nExample: `/trim_audio 00:00:10 00:00:30`")
        return

    start_time = args[1]
    end_time = args[2]

    # Downloading the audio file
    audio = message.reply_to_message.audio
    ms = await message.reply_text("Downloading audio file...")
    try:
        input_file = await client.download_media(
            audio, 
            progress=progress_for_pyrogram, 
            progress_args=("Downloading your audio.", ms, time.time())
        )
    except Exception as e:
        print(e)
        return await ms.edit(f"An error occurred while downloading.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False)

    try:
        await ms.edit("Trimming the audio file...")

        output_file = f"trimmed_{audio.file_name}"

        # Trimming the audio
        trimmed_file = await trim_audio(input_file, output_file, start_time, end_time)
        if trimmed_file:
            # Notify the user that the upload is in progress
            uploader = await ms.edit("Uploading the trimmed audio file...")

            await client.send_audio(
                chat_id=message.chat.id,
                audio=trimmed_file,
                progress=progress_for_pyrogram,
                progress_args=("Uploading audio...", uploader, time.time())
            )
        else:
            await message.reply_text("Failed to process the audio. Please try again later.")
        await uploader.delete()
        try:
            os.remove(trimmed_file)
        except Exception as e:
            print(f"Failed to remove file: {trimmed_file}. Error: {e}")

        try:
            os.remove(input_file)
        except Exception as e:
            print(f"Failed to remove file: {input_file}. Error: {e}")
            
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
