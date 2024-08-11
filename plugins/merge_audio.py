import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import subprocess
import time
from config import Config
from progress import progress

DOWNLOAD_DIR = "/content/Drive_bot/Drive_bot/downloads/"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

user_media_files = {}
user_merge_mode = {}

@Client.on_message(filters.command("merge_audio"))
async def set_merge_audio(client, message: Message):
    user_id = message.from_user.id
    user_merge_mode[user_id] = "audio"
    user_media_files[user_id] = []
    l = await message.reply_text("Send the first audio file.")

@Client.on_message((filters.audio) & ~filters.forwarded)
async def receive_audio(client, message: Message):
    user_id = message.from_user.id
    media_file = message.audio
    start_time = time.time()
    ms = await ms.edit_text("Downloading audio...")

    try:
        media_path = await message.download(
            file_name=f"{DOWNLOAD_DIR}{media_file.file_name}",
            progress=progress,
            progress_args=(ms, start_time, "Downloading audio")
        )

        user_media_files[user_id].append(media_path)

        if len(user_media_files[user_id]) == 1:
            await progress_message.edit_text("First audio received. Now send the second audio.")
        elif len(user_media_files[user_id]) == 2:
            await ms.edit_text("Both audios received. Merging them now...")
            await merge_audios(client, message, user_id)
    except Exception as e:
        await ms.edit_text(f"Error during download: {e}")

async def merge_audios(client, message, user_id):
    audio1, audio2 = user_media_files[user_id]
    output_path = f"{DOWNLOAD_DIR}merged_audio_{user_id}.mp3"

    command = [
        "ffmpeg",
        "-y",  # Add the '-y' flag to overwrite existing files
        "-i", audio1,
        "-i", audio2,
        "-filter_complex", "[0:0][1:0]concat=n=2:v=0:a=1[out]",
        "-map", "[out]",
        output_path
    ]

    start_time = time.time()
    ms = await message.reply_text("Merging audio files...")

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        if os.path.exists(output_path):
            await ms.edit_text("Merging complete, uploading the merged audio...")
            try:
                await message.reply_document(
                    document=output_path,
                    caption="Here is your merged audio file!",
                    progress=progress,
                    progress_args=(ms, start_time, "Uploading merged audio")
                )
            except Exception as e:
                await ms.edit_text(f"Failed to upload the merged audio: {e}")
        else:
            await ms.edit_text("Merging completed, but the output file was not found.")
    else:
        await ms.edit_text(f"Failed to merge: {stderr.decode()}")

    await ms.delete()
    await l.delete()

    # Clean up
    os.remove(audio1)
    os.remove(audio2)
    if os.path.exists(output_path):
        os.remove(output_path)

    # Remove user data
    del user_media_files[user_id]
    del user_merge_mode[user_id]
