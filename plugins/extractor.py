from pyrogram import filters
from pyrogram import Client
from plugins import start 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins import audio
from plugins import merge 
from helper import download 
from config import Config

@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def confirm_dwnld(client, message):
    media = message
    filetype = media.document or media.video or media.audio

    if filetype.mime_type.startswith("video/"):
        await message.reply_text(
            "**What do you want me to do 🤔**",
            quote=True,
            reply_markup=InlineKeyboardMarkup([
                [ InlineKeyboardButton(text="Extract Audio 📢", callback_data="download_file"),
                  InlineKeyboardButton(text="Remove Audio🎧", callback_data="handle_remove_audio")
                ],
                [ InlineKeyboardButton(text="Trim Video ✂️", callback_data="handle_trim_video"),
                  InlineKeyboardButton(text="audio+audio🎵", callback_data="set_merge_audio")
                ],
                [ InlineKeyboardButton(text="Video+audio 📹", callback_data="set_merge_video"),
                  InlineKeyboardButton(text="CANCEL", callback_data="close")
                ]
            ])
        )
    else:
        await message.reply_text(
            "Invalid Media",
            quote=True
        )

user_media_files = {}
user_merge_mode = {}

@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def receive_media(client, message):
    user_id = message.from_user.id

    if user_id not in user_merge_mode:
        await message.reply_text("Please use /merge_audio or /merge_video to start the merging process.")
        return

    merge_mode = user_merge_mode[user_id]
    media_type = 'audio' if message.audio else 'video'
    media_file = getattr(message, media_type, None)

    if media_file:
        start_time = time.time()
        progress_message = await message.reply_text(f"Downloading {media_type}...")

        try:
            media_path = await message.download(
                file_name=f"{DOWNLOAD_DIR}{media_file.file_name}",
                progress=progress,
                progress_args=(progress_message, start_time, f"Downloading {media_type}")
            )

            user_media_files[user_id].append(media_path)

            if merge_mode == "audio":
                if len(user_media_files[user_id]) == 1:
                    await progress_message.edit_text("First audio received. Now send the second audio.")
                elif len(user_media_files[user_id]) == 2:
                    await progress_message.edit_text("Both audios received. Merging them now...")
                    await merge.merge_audios(client, message, user_id)
            elif merge_mode == "video":
                if len(user_media_files[user_id]) == 1 and media_type == "video":
                    await progress_message.edit_text("Video received. Now send the audio file.")
                elif len(user_media_files[user_id]) == 2 and any('.mp4' in file for file in user_media_files[user_id]):
                    await progress_message.edit_text("Both video and audio received. Merging them now...")
                    await merge.merge_video_and_audio(client, message, user_id)

        except Exception as e:
            await progress_message.edit_text(f"Error during download: {e}")

@Client.on_callback_query()
async def cb_handler(client, query):
    data = query.data

    if data == "set_merge_audio":
        user_id = query.from_user.id
        user_merge_mode[user_id] = "audio"
        user_media_files[user_id] = []
        await query.message.edit_text("Send the first audio file.")

    elif data == "set_merge_video":
        user_id = query.from_user.id
        user_merge_mode[user_id] = "video"
        user_media_files[user_id] = []
        await query.message.edit_text("Send the video file.")
