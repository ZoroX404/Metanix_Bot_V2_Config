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
import os
import asyncio
import time
import random
from pyrogram import Client, filters
from moviepy import VideoFileClip

from pyrogram.types import Message

from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix, add_sprefix_suffix, add_prefix_ssuffix, add_sprefix_ssuffix
from helper.ffmpeg import fix_thumb, take_screen_shot
from helper.database import db
from config import Config

app = Client("test", api_id=Config.STRING_API_ID, api_hash=Config.STRING_API_HASH, session_string=Config.STRING_SESSION)

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import MessageMediaType

@Client.on_message(filters.private & filters.command("sv"))
async def sample_video_handler(client, message):
    # Step 1: Check usage
    replied = message.reply_to_message
    if len(message.command) != 2:
        return await message.reply_text("❗ Usage: Reply to a video with `/sv <duration-in-seconds>`", parse_mode="markdown")
    if len(replied.command) != 2:
        return await message.reply_text("❗ Usage: Reply to a video with `/sv <duration-in-seconds>`", parse_mode="markdown")

    # Step 2: Validate replied message
    if not replied:
        return await message.reply("❌ Please reply to a video message when using this command.")

    if not (replied.video or replied.document):
        return await message.reply("❌ This command only works on actual videos or video documents.")

    # Step 3: Parse and validate duration
    try:
        sample_duration = int(message.command[1])
        if sample_duration <= 0:
            return await message.reply("❌ Duration must be a positive number.")
    except ValueError:
        return await message.reply("❌ Duration must be a number.")

    # Step 4: Download the video with progress bar
    file_path = f"downloads/{new_filename}"
    file = replied
    ms = await message.reply_text(text="Trying To Download.....")

    # Use progress bar during the download process
    try:
        path = await client.download_media(message=file, file_name=file_path,  progress=progress_for_pyrogram, progress_args=("**Download Started.... **", ms, time.time()))
        print(f"File downloaded to {path}")
    except Exception as e:
        print(f"Error downloading media: {e}")
        return await ms.edit(e)
        
    try:
        # Step 5: Check video duration
        clip = VideoFileClip(file_path)
        actual_duration = int(clip.duration)
        if sample_duration > actual_duration:
            clip.close()
            os.remove(file_path)
            return await status_msg.edit(f"❌ Given duration is longer than the actual video duration ({actual_duration} seconds).")

        # Step 6: Choose random start time
        max_start = actual_duration - sample_duration
        start_time = random.randint(0, max_start)
        trimmed_path = f"sample_{int(time.time())}_{sample_duration}s.mp4"

        await status_msg.edit(f"✂️ Trimming random {sample_duration}s from {start_time}s...")

        # Use ffmpeg to extract the segment
        cmd = f"ffmpeg -ss {start_time} -i '{file_path}' -t {sample_duration} -c copy '{trimmed_path}' -y"
        process = await asyncio.create_subprocess_shell(cmd)
        await process.communicate()

        # Step 7: Send trimmed video
        await status_msg.edit("📤 Uploading sample video...")
        await message.reply_video(trimmed_path, caption=f"🎬 Random {sample_duration}s sample (from {start_time}s)")

    except Exception as e:
        await status_msg.edit(f"❌ Error: {e}")
    finally:
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(trimmed_path):
            os.remove(trimmed_path)
        if 'clip' in locals():
            clip.close()


    


    
        

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
