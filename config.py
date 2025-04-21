import re
import os
import time

id_pattern = re.compile(r'^.\d+$')


class Config(object):
    # pyro client config
    API_ID = os.environ.get("API_ID", "20089597")  # ⚠️ Required
    API_HASH = os.environ.get("API_HASH", "f96267b63570057fd76e610ab3e79527")  # ⚠️ Required
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7073143219:AAFypnrXjJ6EFCTPkvHd1sIIXE_4Uy9I1XM")
    OWNER = int(os.environ.get("OWNER", "6276548893"))# ⚠️ Required

    # premium 4g renaming client
    STRING_API_ID = os.environ.get("STRING_API_ID", "")
    STRING_API_HASH = os.environ.get("STRING_API_HASH", "")
    STRING_SESSION = os.environ.get("STRING_SESSION", "")

    # database config
    DB_NAME = os.environ.get("DB_NAME", "metanixv2")
    DB_URL = os.environ.get("DB_URL", "mongodb+srv://meta2:meta2@cluster5.oosleu4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster5")  # ⚠️ Required

    # other configs
    BOT_UPTIME = time.time()
    START_PIC = os.environ.get("START_PIC", "https://telegra.ph/file/4d6f2d8ba25b50e9ff0a5.jpg")
    ADMIN = [int(admin) if id_pattern.search(
        admin) else admin for admin in os.environ.get('ADMIN', '7019977613 6276548893 1263768500 5157971857 1257535081 6974925276 6070913153 6030828548').split()]  # ⚠️ Required
    
    FORCE_SUB = os.environ.get("FORCE_SUB", "Animeke14hai") # ⚠️ Required Username without @
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001588776212"))  # ⚠️ Required
    FLOOD = int(os.environ.get("FLOOD", '10'))
    BANNED_USERS = set(int(x) for x in os.environ.get(
        "BANNED_USERS", "1234567890").split())

    # wes response configuration
    WEBHOOK = bool(os.environ.get("WEBHOOK", True))
    PORT = int(os.environ.get("PORT", "8080"))


class Txt(object):
    # part of text configuration
    START_TXT = """<b>Hey {} </b>
    
➻ Tʜɪꜱ Iꜱ Aɴ Aᴅᴠᴀɴᴄᴇᴅ Aɴᴅ Yᴇᴛ Pᴏᴡᴇʀꜰᴜʟ Aɴᴅ Aᴅᴠᴀɴᴄᴇ Mᴇᴛᴀᴅᴀᴛᴀ Rᴇɴᴀᴍᴇʀ.⚡️

➻ Uꜱɪɴɢ Tʜɪꜱ Bᴏᴛ Yᴏᴜ Cᴀɴ Rᴇɴᴀᴍᴇ Aɴᴅ Cʜᴀɴɢᴇ Tʜᴜᴍʙɴᴀɪʟ Oғ Yᴏᴜʀ Fɪʟᴇꜱ.🖼

➻ Yᴏᴜ Cᴀɴ Aʟꜱᴏ Cᴏɴᴠᴇʀᴛ Vɪᴅᴇᴏ Tᴏ Fɪʟᴇ Aɴᴅ Fɪʟᴇ Tᴏ Vɪᴅᴇᴏ.📁»🎬

➻ Tʜɪꜱ Bᴏᴛ Aʟꜱᴏ Sᴜᴘᴘᴏʀᴛꜱ Cᴜꜱᴛᴏᴍ Tʜᴜᴍʙɴᴀɪʟ, Cᴀᴘᴛɪᴏɴ Aɴᴅ Mᴇᴛᴀᴅᴀᴛᴀ.✏️
"""

    ABOUT_TXT = """<b>╭───────────────⍟
├<b> My Name</b> : 𝘔𝘦𝘵𝘢𝘕𝘪𝘟
├<b> Created by</b> : 𝘈𝘑
├<b> Library</b> : <a href=https://github.com/pyrogram>Pyrogram</a>
├<b> Language</b> : <a href=https://www.python.org>Python 3</a>
├<b> Database</b> : <a href=https://cloud.mongodb.com>Mongo DB</a>
╰───────────────⍟ """

    HELP_TXT = """
🖼 <b><u>Hᴏᴡ Tᴏ Sᴇᴛ Tʜᴜᴍʙɴɪʟᴇ</u></b>
  
<b>•></b> /start Tʜᴇ Bᴏᴛ Aɴᴅ Sᴇɴᴅ Aɴy Pʜᴏᴛᴏ Tᴏ Aᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟy Sᴇᴛ Tʜᴜᴍʙɴɪʟᴇ.
<b>•></b> /del_thumb Uꜱᴇ Tʜɪꜱ Cᴏᴍᴍᴀɴᴅ Tᴏ Dᴇʟᴇᴛᴇ Yᴏᴜʀ Oʟᴅ Tʜᴜᴍʙɴɪʟᴇ.
<b>•></b> /view_thumb Uꜱᴇ Tʜɪꜱ Cᴏᴍᴍᴀɴᴅ Tᴏ Vɪᴇᴡ Yᴏᴜʀ Cᴜʀʀᴇɴᴛ Tʜᴜᴍʙɴɪʟᴇ.


📜 <b><u>Hᴏᴡ Tᴏ Sᴇᴛ Cᴜꜱᴛᴏᴍ Cᴀᴩᴛɪᴏɴ</u></b>

<b>•></b> /set_caption - Tᴏ Sᴇᴛ ᴀ Cᴜꜱᴛᴏᴍ Cᴀᴩᴛɪᴏɴ
<b>•></b> /see_caption - Tᴏ Vɪᴇᴡ Yᴏᴜʀ Cᴜꜱᴛᴏᴍ Cᴀᴩᴛɪᴏɴ
<b>•></b> /del_caption - Tᴏ Dᴇʟᴇᴛᴇ Yᴏᴜʀ Cᴜꜱᴛᴏᴍ Cᴀᴩᴛɪᴏɴ
Exᴀᴍᴩʟᴇ:- <code> /set_caption 📕 Fɪʟᴇ Nᴀᴍᴇ: {filename}
💾 Sɪᴢᴇ: {filesize}
⏰ Dᴜʀᴀᴛɪᴏɴ: {duration} </code>

✏️ <b><u>Hᴏᴡ Tᴏ Rᴇɴᴀᴍᴇ A Fɪʟᴇ</u></b>
<b>•></b> Sᴇɴᴅ Aɴy Fɪʟᴇ Aɴᴅ Tyᴩᴇ Nᴇᴡ Fɪʟᴇ Nɴᴀᴍᴇ \nAɴᴅ Aᴇʟᴇᴄᴛ Tʜᴇ Fᴏʀᴍᴀᴛ [ document, video, audio ].           

⚙ <b><u>Aᴅᴠᴀɴᴄᴇ Rᴇɴᴀᴍᴇ + Mᴇᴛᴀᴅᴀᴛᴀ</u></b>
/metadata - To Set & Change your metadata code
/set_prefix - To Set Your Prefix
/del_prefix - Delete Your Prefix
/see_prefix - To See Your Prefix
/set_suffix - To Set Your Suffix
/see_suffix - To See Your Suffix
/del_suffix - Delete Your Suffix

"""

    SEND_METADATA = """
❪ <b>𝘚𝘦𝘯𝘥 𝘠𝘰𝘶𝘳 𝘊𝘶𝘴𝘵𝘰𝘮 𝘔𝘦𝘵𝘢𝘥𝘢𝘵𝘢</b> ❫

Fᴏʀ Exᴀᴍᴘʟᴇ:-

◦ <code>  -map 0 -c:s copy -c:a copy -c:v copy -metadata title="Created By:- 𝘈𝘑" -metadata author="𝘈𝘑" -metadata:s:s title="Subtitled By :- @MetaNiXbot" -metadata:s:a title="By :- @MetaNiXbot" -metadata:s:v title="By:- 𝘈𝘑" </code>

Note - Only Customize Text between "__" which is located after 'title='
"""

    PROGRESS_BAR = """<b>\n
╭━━━━❰ᴘʀᴏɢʀᴇss ʙᴀʀ❱━➣
┣⪼ 🔗 Sɪᴢᴇ: {1} | {2}
┣⪼ ✅ Dᴏɴᴇ : {0}%
┣⪼ ⚡ Sᴩᴇᴇᴅ: {3}/s
┣⪼ 🕰 Eᴛᴀ: {4}
╰━━━━━━━━━━━━━━━➣ </b>"""
