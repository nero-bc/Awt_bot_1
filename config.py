import os, time

class Config(object):
    # Audio-_edit_bot client Config 
    API_ID = os.getenv("API_ID", "21740783")
    API_HASH = os.getenv("API_HASH", "a5dc7fec8302615f5b441ec5e238cd46")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "7496680438:AAHyEZDGnIoARpfywrzQOhB27un9pja49p4")
    
    # Database config
    DB_NAME = os.environ.get("DB_NAME", "Speedwolf1")     
    DB_URL  = os.environ.get("DB_URL", "mongodb+srv://Speedwolf1:speedwolf24689@cluster0.rgfywsf.mongodb.net/")
    
    # Other configs
    BOT_UPTIME  = time.time()
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
    START_PIC   = os.environ.get("START_PIC", "https://telegra.ph/file/feb6dd0a1cb8576943c0f.jpg")
    
    # Web response configuration     
    WEBHOOK = bool(os.environ.get("WEBHOOK", "True"))
    
    ADMIN   = [int(os.environ.get("ADMIN", "6299192020"))]  # Closed the square bracket here
    
class Txt(object):
    
    START_TXT = """Hello Friends I am The Advanced 📹Video Editor bot. I have special features like "Audio remover" and "Video trimmer."
    
</a>"\n Bot Is Made By @Anime_Warrior_Tamil"</b>"""
    
    ABOUT_TXT = f"""<b>😈 My Name :</b> <a href='https://t.me/Gjjbsrijjb_bot'>Video Editor Bot ⚡</a>
<b>📝 Language :</b> <a href='https://python.org'>Python 3</a>
<b>📚 Library :</b> <a href='https://pyrogram.org'>Pyrogram 2.0</a>
<b>🚀 Server :</b> <a href='https://heroku.com'>Heroku</a>
<b>📢 Channel :</b> <a href='https://t.me/Anime_Warrior_Tamil'>AWT BOTS</a>
<b>🛡️ :</b> <a href='https://t.me/+NITVxLchQhYzNGZl'>AWT Developer</a>
    
<b>😈 Bot Made By :</b> @AWT_Bot_Developer"""


    HELP_TXT = """
<b><u>Video Editor Bot Commands</u></b>
  
<b>•»</b> /start Use this command to check if the bot is alive ✅.
<b>•»</b> /remove_audio Use this command to remove audio.
<b>•»</b> /trim_video Use this command to trim video.

✏️ <b><u>How To Use the Bot</u></b>

<b>•»</b> Reply to a video to remove audio or trim video.          

ℹ️ Any other help, contact: <a href=https://t.me/AWT_bots_developer>Bot Developer</a>
"""

    # ⚠️ Don't Remove Our Credits @ILLGELA_DEVELOPER🙏🥲
    DEV_TXT = """hiiiiiiiiiii"""
    
    PROGRESS_BAR = """\n
<b>📁 Size</b> : {1} | {2}
<b>⏳️ Done</b> : {0}%
<b>🚀 Speed</b> : {3}/s
<b>⏰️ ETA</b> : {4} """
