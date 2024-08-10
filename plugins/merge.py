import os
import asyncio
from pyrogram import Client
import subprocess
import time
from config import Config
from progress import progress

DOWNLOAD_DIR = "/content/Drive_bot/Drive_bot/downloads/"

async def merge_audios(client, message, user_id):
    audio1, audio2 = user_media_files[user_id]
    output_path = f"{DOWNLOAD_DIR}merged_audio_{user_id}.mp3"

    command = [
        "ffmpeg",
        "-y",
        "-i", audio1,
        "-i", audio2,
        "-filter_complex", "[0:0][1:0]concat=n=2:v=0:a=1[out]",
        "-map", "[out]",
        output_path
    ]

    start_time = time.time()
    progress_message = await message.reply_text("Merging audio files...")

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        if os.path.exists(output_path):
            await progress_message.edit_text("Merging complete, uploading the merged audio...")
            try:
                await message.reply_document(
                    document=output_path,
                    caption="Here is your merged audio file!",
                    progress=progress,
                    progress_args=(progress_message, start_time, "Uploading merged audio")
                )
            except Exception as e:
                await progress_message.edit_text(f"Failed to upload the merged audio: {e}")
        else:
            await progress_message.edit_text("Merging completed, but the output file was not found.")
    else:
        await progress_message.edit_text(f"Failed to merge: {stderr.decode()}")

    os.remove(audio1)
    os.remove(audio2)
    if os.path.exists(output_path):
        os.remove(output_path)

    del user_media_files[user_id]
    del user_merge_mode[user_id]

async def merge_video_and_audio(client, message, user_id):
    video, audio = user_media_files[user_id]
    output_path = f"{DOWNLOAD_DIR}merged_video_{user_id}.mp4"

    command = [
        "ffmpeg",
        "-y",
        "-i", video,
        "-i", audio,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        output_path
    ]

    start_time = time.time()
    progress_message = await message.reply_text("Merging video and audio...")

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        if os.path.exists(output_path):
            await progress_message.edit_text("Merging complete, uploading the merged video...")
            try:
                await message.reply_document(
                    document=output_path,
                    caption="Here is your merged video file!",
                    progress=progress,
                    progress_args=(progress_message, start_time, "Uploading merged video")
                )
            except Exception as e:
                await progress_message.edit_text(f"Failed to upload the merged video: {e}")
        else:
            await progress_message.edit_text("Merging completed, but the output file was not found.")
    else:
        await progress_message.edit_text(f"Failed to merge: {stderr.decode()}")

    os.remove(video)
    os.remove(audio)
    if os.path.exists(output_path):
        os.remove
