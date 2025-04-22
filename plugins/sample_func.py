import random
import asyncio
import os
import time
import shutil  # Optional cleanup
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, Message
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image

from pyrogram.types import Message

from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix, add_sprefix_suffix, add_prefix_ssuffix, add_sprefix_ssuffix
from helper.ffmpeg import fix_thumb, take_screen_shot
from helper.database import db
from config import Config

app = Client("test", api_id=Config.STRING_API_ID, api_hash=Config.STRING_API_HASH, session_string=Config.STRING_SESSION)

@Client.on_message(filters.private & filters.command("sv") & filters.reply)
async def sample_video_handler(bot: Client, message: Message):
    replied = message.reply_to_message
    if replied.document:
        media = replied.video
    if replied.document:
        media = replied.docment
    else:
        return await message.reply("❌ This command only works on actual videos or video documents.")

    try:
        command_parts = message.text.split()
        if len(command_parts) < 2 or len(command_parts) > 2:
            await message.reply("meow1")
            raise ValueError
        sample_duration = int(command_parts[1])
        if sample_duration <= 0:
            await message.reply("meow2")
            raise ValueError
    except (IndexError, ValueError):
        return await message.reply("❗ Usage: Reply to a video with `/sv <duration-in-seconds>`")
    
        

    # Ensure it's a video or video document
    # if replied.video:
    #     media = replied.video
    # elif replied.document and replied.document.mime_type and replied.document.mime_type.startswith("video"):
    #     media = replied.document
    # else:
    #     return await message.reply("❌ This command only works on actual videos or video documents.")

    # # Parse sample duration from command
    # try:
    #     command_parts = message.text.split()
    #     if len(command_parts) < 2:
    #         raise ValueError
    #     sample_duration = int(command_parts[1])
    #     if sample_duration <= 0:
    #         raise ValueError
    # except (IndexError, ValueError):
    #     return await message.reply("❗ Usage: Reply to a video with `/sv <duration-in-seconds>`")

    # msg = await message.reply("📥 Downloading media...")

    # file_id = media.file_id
    # input_path = f"downloads/{file_id}"
    # output_path = f"downloads/sample_{file_id}.mkv"

    # # Ensure the downloads directory exists
    # try:
    #     os.makedirs("downloads", exist_ok=True)
    # except Exception as e:
    #     return await msg.edit(f"❌ Failed to create downloads directory: {e}")

    # try:
    #     await bot.download_media(replied, file_name=input_path)
    # except Exception as e:
    #     return await msg.edit(f"❌ Failed to download: {e}")

    # # Get total duration of the video
    # try:
    #     parser = createParser(input_path)
    #     metadata = extractMetadata(parser)
    #     if metadata and metadata.has("duration"):
    #         total_duration = metadata.get("duration").seconds
    #     else:
    #         return await msg.edit("❌ Could not determine video duration.")
    # except Exception as e:
    #     return await msg.edit(f"❌ Error reading metadata: {e}")

    # if sample_duration >= total_duration:
    #     return await msg.edit(
    #         f"⚠️ The video is only {total_duration}s long. You requested {sample_duration}s."
    #     )

    # # Pick a random start time for the sample
    # try:
    #     start_time = random.randint(0, total_duration - sample_duration)
    # except ValueError:
    #     return await msg.edit("❌ Could not calculate start time for trimming.")

    # await msg.edit(f"✂️ Trimming from **{start_time}s** out of {total_duration}s...")

    # # Run FFmpeg to trim the video
    # cmd = f'ffmpeg -y -ss {start_time} -i "{input_path}" -t {sample_duration} -c copy "{output_path}"'
    # process = await asyncio.create_subprocess_shell(
    #     cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    # )
    # stdout, stderr = await process.communicate()

    # # Check if the command executed properly
    # if process.returncode != 0 or not os.path.exists(output_path):
    #     return await msg.edit(f"❌ FFmpeg Error: {stderr.decode() if stderr else 'Unknown error'}")

    # await msg.edit("📤 Uploading sample...")

    # try:
    #     await bot.send_video(
    #         chat_id=message.chat.id,
    #         video=output_path,
    #         caption=f"🎬 Random sample ({sample_duration}s from {start_time}s)",
    #         reply_to_message_id=message.reply_to_message.id
    #     )
    # except Exception as e:
    #     return await msg.edit(f"❌ Upload failed: {e}")

    # await msg.delete()

    # # Cleanup
    # try:
    #     if os.path.exists(input_path):
    #         os.remove(input_path)
    #     if os.path.exists(output_path):
    #         os.remove(output_path)
    # except Exception as e:
    #     print(f"Cleanup failed: {e}")
