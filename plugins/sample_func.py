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


@Client.on_message(filters.private & filters.command("sv") & filters.reply & filters.user(Config.ADMIN))
async def sample_random_segment(bot: Client, message: Message):
    replied = message.reply_to_message

    # Ensure it's a .mp4 video or document
    is_video = replied.video and replied.video.file_name and replied.video.file_name.endswith(".mp4")
    is_doc_mp4 = replied.document and replied.document.file_name and replied.document.file_name.endswith(".mp4")

    if not (is_video or is_doc_mp4):
        return await message.reply("❗ Please reply to a video or .mp4 document.")

    # Get duration from command
    try:
        sample_duration = int(message.command[1])
        if sample_duration <= 0:
            raise ValueError
    except (IndexError, ValueError):
        return await message.reply("❗ Usage: Reply to a .mp4 with `/sv <duration-in-seconds>`")

    msg = await message.reply("📥 Downloading media...")

    media = replied.video or replied.document
    file_id = media.file_id
    input_path = f"downloads/{file_id}.mp4"
    output_path = f"downloads/sample_{file_id}.mp4"

    try:
        await bot.download_media(replied, file_name=input_path)
    except Exception as e:
        return await msg.edit(f"❌ Failed to download: {e}")

    # Extract full duration
    try:
        parser = createParser(input_path)
        metadata = extractMetadata(parser)
        if metadata.has("duration"):
            total_duration = metadata.get("duration").seconds
        else:
            return await msg.edit("❌ Could not determine video duration.")
        parser.close()
    except Exception as e:
        return await msg.edit(f"❌ Error reading metadata: {e}")

    if sample_duration >= total_duration:
        return await msg.edit(
            f"⚠️ The video is only {total_duration}s long. You requested {sample_duration}s."
        )

    # Pick random start time
    start_time = random.randint(0, total_duration - sample_duration)
    await msg.edit(f"✂️ Trimming from **{start_time}s** out of {total_duration}s...")

    # Run ffmpeg to trim
    cmd = f'ffmpeg -y -ss {start_time} -i "{input_path}" -t {sample_duration} -c copy "{output_path}"'
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()

    if not os.path.exists(output_path):
        return await msg.edit("❌ Failed to trim the video.")

    await msg.edit("📤 Uploading sample...")

    try:
        await bot.send_video(
            message.chat.id,
            video=output_path,
            caption=f"🎬 Random sample ({sample_duration}s from {start_time}s)",
            reply_to_message_id=message.id
        )
    except Exception as e:
        return await msg.edit(f"❌ Upload failed: {e}")

    await msg.delete()
    os.remove(input_path)
    os.remove(output_path)

