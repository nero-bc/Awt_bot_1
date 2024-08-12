from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins import merge_audio, merge_video, audio  # Import from merge.py
from helper import download 
from config import Config

@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def confirm_dwnld(client, message):
    media = message
    filetype = media.document or media.video or media.audio

    if filetype:
        if filetype.mime_type.startswith("video/"):
            await message.reply_text(
                "**What do you want me to do with this file 🤔**",
                quote=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="Extract Audio 📢", callback_data="download_file"),
                     InlineKeyboardButton(text="Remove Audio 🎧", callback_data="handle_remove_audio")],
                    [InlineKeyboardButton(text="Trim Video ✂️", callback_data="handle_trim_video"),
                     InlineKeyboardButton(text="audio+audio 🎵", callback_data="set_merge_audio")],
                    [InlineKeyboardButton(text="Video+audio 📹", callback_data="set_merge_video"),
                     InlineKeyboardButton(text="Trim audio ✂️", callback_data="handle_trim_audio")]
                    [InlineKeyboardButton(text="Close❌", callback_data="close")]
                ])
            )
        elif filetype.mime_type.startswith("audio/"):
            await message.reply_text(
                "What do you want me to do with this audio file 🤨",
                quote=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="Audio+audio 🎵", callback_data="set_merge_audio"),
                     InlineKeyboardButton(text="Trim Audio ✂️", callback_data="handle_trim_audio")],
                    [InlineKeyboardButton(text="CLOSE ❌", callback_data="close")]
                ])
            )
        else:
            await message.reply_text(
                "Invalid Media",
                quote=True
            )
    else:
        await message.reply_text(
            "No media file detected",
            quote=True
                                         )
