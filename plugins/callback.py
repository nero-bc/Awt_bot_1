from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.merge import set_merge_audio, set_merge_video  # Import from merge.py
from plugins import start, audio
from helper.progress import PRGRS
from helper.tools import clean_up
from config import Config, Txt
from plugins.audio import handle_remove_audio
from helper.download import download_file, DATA
from helper.ffmpeg import extract_audio, extract_subtitle
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@Client.on_callback_query()
async def cb_handler(client, query):
    data = query.data

    if data == "start_data":
        await query.answer()
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⚔️Update Channel", url="https://t.me/Anime_Warrior_Tamil"),
                InlineKeyboardButton("🛡️Support Group", url="https://t.me/+NITVxLchQhYzNGZl")
            ],
            [
                InlineKeyboardButton("📢Help", callback_data="help"),
                InlineKeyboardButton("⚡About", callback_data="about")
            ],
            [
                InlineKeyboardButton("❌Close", callback_data="close")
            ]
        ])

        await query.message.edit_text(
            text=Txt.START_TXT.format(query.from_user.mention),
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        return
    elif data == "help":
        await query.answer()
        keyboard = InlineKeyboardMarkup([[
                # Don't change the owner details if you change the bot not work  #
                InlineKeyboardButton("😈 ᴏᴡɴᴇʀ", url="https://t.me/Devilo7")
                ],[
                InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data = "close"),
                InlineKeyboardButton("⏪ Bᴀᴄᴋ", callback_data = "start")
            ]]) 
        
        await query.message.edit_text(
            text=Txt.HELP_TXT,
            disable_web_page_preview=True,
        )
        return
    elif data == "about":
        await query.answer()
        keyboard = InlineKeyboardMarkup([[
                #⚠️ Don't change the owner details if you change the bot not work ⚠️ #
                InlineKeyboardButton("😈 ᴏᴡɴᴇʀ", url="https://t.me/Devilo7")
                ],[
                InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data = "close"),
                InlineKeyboardButton("⏪ Bᴀᴄᴋ", callback_data = "start")
            ]])  

        await query.message.edit_text(
            text=Txt.ABOUT_TXT.format(client.mention),
            disable_web_page_preview = True,
        )
        return

    elif data == "download_file":
        await query.answer()
        await query.message.delete()
        await download_file(client, query.message)

    elif data == "handle_remove_audio":
        await query.answer()
        await handle_remove_audio(client, query.message)
        await query.message.delete()

    elif data == "handle_trim_video":
        await query.answer()
        await query.message.reply_text("Please use the command in the format: /trim_video <start_time> <end_time>.\nExample: /trim_video 00:00:10 00:00:20")
        await query.message.delete()

    elif data == "set_merge_audio":
        await query.answer()
        await set_merge_audio(client, query.message)  # Use the function from merge.py
        await query.message.delete()

    elif data == "set_merge_video":
        await query.answer()
        await set_merge_video(client, query.message)  # Use the function from merge.py
        await query.message.delete()

    elif data == "progress_msg":
        try:
            msg = "Progress Details...\n\nCompleted : {current}\nTotal Size : {total}\nSpeed : {speed}\nProgress : {progress:.2f}%\nETA: {eta}"
            await query.answer(
                msg.format(
                    **PRGRS[f"{query.message.chat.id}_{query.message.message_id}"]
                ),
                show_alert=True
            )
        except:
            await query.answer(
                "Processing your file...", msg,
                show_alert=True
            )

    elif data.startswith('audio'):
        await query.answer()
        try:
            _, mapping, keyword = data.split('_')
            audio_data = DATA[keyword][int(mapping)]
            await extract_audio(client, query.message, audio_data)
        except KeyError:
            await query.message.edit_text("**Details Not Found**")

    elif data.startswith('subtitle'):
        await query.answer()
        try:
            _, mapping, keyword = data.split('_')
            subtitle_data = DATA[keyword][int(mapping)]
            await extract_subtitle(client, query.message, subtitle_data)
        except KeyError:
            await query.message.edit_text("**Details Not Found**")

    elif data.startswith('cancel'):
        try:
            query_type, mapping, keyword = data.split('_')
            data = DATA[keyword][int(mapping)] 
            await clean_up(data['location'])  
            await query.message.edit_text("**Cancelled...**")
            await query.answer(
                "Cancelled...",
                show_alert=True
            ) 
        except:
            await query.answer() 
            await query.message.edit_text("**Details Not Found**")        
