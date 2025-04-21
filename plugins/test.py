import random
import asyncio
import os
import time
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image

from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix, add_sprefix_suffix, add_prefix_ssuffix, add_sprefix_ssuffix
from helper.ffmpeg import fix_thumb, take_screen_shot
from helper.database import db
from config import Config

app = Client("test", api_id=Config.STRING_API_ID, api_hash=Config.STRING_API_HASH, session_string=Config.STRING_SESSION)


@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def rename(bot, message):
    print("Received a message!")
    print("From user:", message.from_user.id)

    if message.from_user.id not in Config.ADMIN:
        await message.reply_text("**Access Denied** ⚠️ \nError: You are not authorized to use my features")
        return

    await message.reply_text("meow")
