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
      
def trim_video(input_file, start_time, end_time, output_file):
    command = [
        'ffmpeg', '-i', input_file,
        '-ss', start_time,
        '-to', end_time,
        '-c:v', 'copy',  # copy video stream
        '-c:a', 'copy',  # copy audio stream
        '-map_metadata', '0', '-movflags', 'use_metadata_tags',
        output_file
    ]
    success, output = run_command(command)
    if not success:
        print(f"Failed to trim video: {output}", file=sys.stderr)
    return success

async def get_video_details(file_path):
    command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size', '-of', 'default=noprint_wrappers=1', file_path]
    success, output = run_command(command)
    if success:
        details = {}
        for line in output.splitlines():
            key, value = line.split('=')
            details[key] = value
        return details
    return None

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

@Client.on_message(filters.command("trim_video"))
async def handle_trim_video(client, message):
    args = message.command
    if len(args) != 3:
        await message.reply_text("Usage: /trim_video <start_time> <end_time>\nExample: /trim_video 00:00:10 00:00:20")
        return

    if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.document):
        await message.reply_text("Please reply to a video or document message with the /trim_video command.")
        return

    start_time = args[1]
    end_time = args[2]
    media = message.reply_to_message.video or message.reply_to_message.document
    ms = await message.reply_text("Downloading media...")

    try:
        file_path = await client.download_media(
            media, 
            progress=progress_for_pyrogram, 
            progress_args=("Downloading your video.", ms, time.time())
        ) 

    except Exception as e:
        print(e)
        return await ms.edit(f"An error occurred while downloading.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False) 
    
    try:
        await ms.edit_text("Processing your file ...")

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file_trimmed = tempfile.mktemp(suffix=f"_{base_name}_trimmed.mp4")

        future = executor.submit(trim_video, file_path, start_time, end_time, output_file_trimmed)
        success = future.result()

        if success:
            details = await get_video_details(output_file_trimmed)
            if details:
                duration = details.get('duration', 'Unknown')
                size = details.get('size', 'Unknown')
                size_mb = round(int(size) / (1024 * 1024), 2)
                duration_sec = round(float(duration))
                caption = f"Here's your trimmed video file. Duration: {duration_sec} seconds. Size: {size_mb} MB"
                
                # Get the current event loop
                loop = asyncio.get_event_loop()
                
                # Create thumbnail with duration, size, and play button
                thumbnail_path = tempfile.mktemp(suffix=f"_{base_name}_thumb.png")
                thumbnail = await loop.run_in_executor(executor, create_thumbnail, output_file_trimmed, thumbnail_path, duration_sec, int(size))
                
                uploader = await ms.edit_text("Uploading video..")

                await client.send_video(
                    chat_id=message.chat.id,
                    video=output_file_trimmed,
                    caption=caption,
                    thumb=thumbnail,
                    progress=progress_for_pyrogram,
                    progress_args=("Uploading Video...", uploader, time.time())
                )
            else:
                await message.reply_text("Failed to retrieve video details.")
        else:
            await message.reply_text("Failed to process the video. Please try again later.")
        await uploader.delete()
        
        # Clean up files
        try:
            os.remove(file_path)
        except Exception as e:
            logging.error(f"Failed to remove file: {file_path}. Error: {e}")

        try:
            os.remove(output_file_trimmed)
        except Exception as e:
            logging.error(f"Failed to remove file: {output_file_trimmed}. Error: {e}")
            
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
