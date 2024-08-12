import os
import tempfile
import subprocess
import sys
import math
import time
import asyncio
import logging 
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
from pyrogram import Client, filters
from plugins import start
from helper.utils import progress_for_pyrogram
from plugins import extractor 
from pyrogram.errors import FloodWait
from PIL import Image, ImageDraw  # Importing PIL for image processing

app = Flask(__name__)

# Thread pool for async processing
executor = ThreadPoolExecutor(max_workers=4)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {e.stderr.decode('utf-8')}")
        return False, e.stderr.decode('utf-8')

def remove_audio(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, '-c:v', 'copy', '-an', '-map_metadata', '0', '-movflags', 'use_metadata_tags', output_file]
    success, _ = run_command(command)
    return success

def get_video_duration(file_path):
    command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
    success, output = run_command(command)
    if success:
        try:
            return float(output.strip())
        except ValueError:
            logging.error("Failed to parse duration output")
            return 0
    return 0

def create_play_button_image():
    # Create a blank image with a transparent background
    size = (100, 100)
    play_button_img = Image.new("RGBA", size, (0, 0, 0, 0))

    # Draw a play button (triangle) on the image
    draw = ImageDraw.Draw(play_button_img)
    triangle = [(25, 20), (25, 80), (75, 50)]
    draw.polygon(triangle, fill="white")

    # Save the image as play_button.png
    play_button_path = tempfile.mktemp(suffix=".png")
    play_button_img.save(play_button_path)

    return play_button_path

def create_thumbnail(input_file, output_thumbnail, duration, size):
    # Extract a thumbnail from the video
    command_thumbnail = ['ffmpeg', '-i', input_file, '-ss', '00:00:05', '-vframes', '1', output_thumbnail]
    success, _ = run_command(command_thumbnail)
    
    if success:
        # Convert duration to MM:SS format
        total_seconds = int(duration)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        duration_text = f"{minutes:02}:{seconds:02}"

        # Calculate file size in MB
        size_mb = round(int(size) / (1024 * 1024), 2)
        size_text = f"{size_mb} MB"
        
        output_with_text = output_thumbnail.replace('.png', '_with_text.png')
        command_text = [
            'ffmpeg', '-i', output_thumbnail, '-vf',
            f"drawtext=text='{duration_text}':x=W-tw-10:y=10:fontcolor=white:fontsize=24, drawtext=text='{size_text}':x=W-tw-10:y=H-th-40:fontcolor=white:fontsize=24",
            output_with_text
        ]
        success, _ = run_command(command_text)
        
        if success:
            # Overlay play button
            play_button_path = create_play_button_image()  # Generate play button image
            final_output_thumbnail = output_thumbnail.replace('.png', '_final.png')
            command_overlay = [
                'ffmpeg', '-i', output_with_text, '-i', play_button_path, '-filter_complex',
                "overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2", final_output_thumbnail
            ]
            success, _ = run_command(command_overlay)
            
            if success:
                return final_output_thumbnail
    return None

@Client.on_message(filters.command("remove_audio"))
async def handle_remove_audio(client, message):
    if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.document):
        await message.reply_text("Please reply to a video or document message with the /remove_audio command.")
        return

    media = message.reply_to_message.video or message.reply_to_message.document
    ms = await message.reply_text("Downloading media...")

    try:
        file_path = await client.download_media(
            media, 
            progress=progress_for_pyrogram, 
            progress_args=("Downloading started..", ms, time.time())
        )
    except Exception as e:
        print(e)
        return await ms.edit(f"An error occurred while downloading.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False) 
    
    try:
        await ms.edit_text("Please wait processing...")

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file_no_audio = tempfile.mktemp(suffix=f"_{base_name}_noaudio.mp4")

        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(executor, remove_audio, file_path, output_file_no_audio)

        if success:
            duration = get_video_duration(output_file_no_audio)
            size = os.path.getsize(output_file_no_audio)
            caption = f"Here's your cleaned video file. Duration: {round(duration)} seconds. Size: {round(size / (1024 * 1024), 2)} MB"
                
            # Create thumbnail with duration, size, and play button
            thumbnail_path = tempfile.mktemp(suffix=f"_{base_name}_thumb.png")
            thumbnail = await loop.run_in_executor(executor, create_thumbnail, output_file_no_audio, duration, size)
                
            if thumbnail:
                uploader = await ms.edit_text("Uploading media...")
                await client.send_video(
                    chat_id=message.chat.id,
                    caption=caption,
                    video=output_file_no_audio,
                    thumb=thumbnail,
                    progress=progress_for_pyrogram,
                    progress_args=("Uploading...", uploader, time.time())
                )
            else:
                await message.reply_text("Failed to generate thumbnail. Please try again later.")
        else:
            await message.reply_text("Failed to process the video. Please try again later.")
        
        await uploader.delete()

        # Safely remove files
        try:
            os.remove(file_path)
        except Exception as e:
            logging.error(f"Failed to remove file: {file_path}. Error: {e}")

        try:
            os.remove(output_file_no_audio)
        except Exception as e:
            logging.error(f"Failed to remove file: {output_file_no_audio}. Error: {e}")
            
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
