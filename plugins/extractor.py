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

    if filetype.mime_type.startswith("video/") or filetype.mime_type.startswith("audio/"):
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
