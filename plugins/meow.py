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

# @Client.on_message(filters.private & filters.command("sv"))
# async def sample_video_handler(client, message):
#     print(f"Command received: {message.command}")
#     print(f"Command length: {len(message.command)}")
    
#     # Step 1: Check usage
#     replied = message.reply_to_message
#     print(f"Has replied message: {replied is not None}")
    
#     if not replied:
#         print("No replied message found")
#         return await message.reply("❌ Please reply to a video message when using this command.")
    
#     # Check if duration is provided
#     if len(message.command) == 1:  # Only "/sv" without any parameter
#         print("Command used without parameters")
#         return await message.reply("❗ Usage: Reply to a video with `/sv <duration-in-seconds>`", parse_mode="markdown")
        
#     # Check if more than one parameter is provided
#     if len(message.command) > 2:
#         print(f"Too many parameters: {message.command[1:]}")
#         return await message.reply("❗ Usage: Reply to a video with `/sv <duration-in-seconds>` (only one number)", parse_mode="markdown")
        
#     # Step 2: Validate replied message
#     print(f"Replied message type - video: {replied.video is not None}, document: {replied.document is not None}")
#     if not (replied.video or replied.document):
#         print("Replied message is not a video or document")
#         return await message.reply("❌ This command only works on actual videos or video documents.")
        
#     # Step 3: Parse and validate duration
#     try:
#         print(f"Trying to parse duration: {message.command[1]}")
#         sample_duration = int(message.command[1])
#         print(f"Parsed duration: {sample_duration}")
#         if sample_duration <= 0:
#             print("Duration is not positive")
#             return await message.reply("❌ Duration must be a positive number.")
#     except ValueError:
#         print(f"Failed to parse '{message.command[1]}' as an integer")
#         return await message.reply("❌ Duration must be a number.")
        
#     # Step 4: Download the video with progress bar
#     new_filename = f"video_{message.from_user.id}_{int(time.time())}.mp4"
#     file_path = f"downloads/{new_filename}"
    
#     # Ensure downloads directory exists
#     os.makedirs("downloads", exist_ok=True)
#     print(f"Downloading to: {file_path}")
    
#     # Use progress bar during the download process
#     status_msg = await message.reply_text("Trying to download...")
#     try:
#         path = await client.download_media(
#             message=replied,
#             file_name=file_path,
#             progress=progress_for_pyrogram, 
#             progress_args=("**Download Started... **", status_msg, time.time())
#         )
#         print(f"File downloaded to {path}")
#     except Exception as e:
#         print(f"Error downloading media: {e}")
#         return await status_msg.edit(f"❌ Download error: {str(e)}")
        
#     try:
#         # Step 5: Check video duration
#         print(f"Analyzing video at {path}")
#         clip = VideoFileClip(path)
#         actual_duration = int(clip.duration)
#         print(f"Video duration: {actual_duration}s")
        
#         if sample_duration > actual_duration:
#             print(f"Requested duration ({sample_duration}s) exceeds video length ({actual_duration}s)")
#             clip.close()
#             os.remove(path)
#             return await status_msg.edit(f"❌ Given duration ({sample_duration}s) is longer than the actual video duration ({actual_duration}s).")
            
#         # Step 6: Choose random start time
#         max_start = actual_duration - sample_duration
#         start_time = random.randint(0, max_start)
#         trimmed_path = f"downloads/sample_{message.from_user.id}_{int(time.time())}_{sample_duration}s.mp4"
#         print(f"Selected segment: {start_time}s to {start_time + sample_duration}s")
#         print(f"Output will be saved to: {trimmed_path}")
        
#         await status_msg.edit(f"✂️ Trimming random {sample_duration}s segment from {start_time}s...")
        
#         # Use ffmpeg to extract the segment
#         cmd = f'ffmpeg -ss {start_time} -i "{path}" -t {sample_duration} -c copy "{trimmed_path}" -y'
#         print(f"Running command: {cmd}")
#         process = await asyncio.create_subprocess_shell(cmd)
#         await process.communicate()
#         print("FFmpeg processing complete")
        
#         # Step 7: Send trimmed video
#         await status_msg.edit("📤 Uploading sample video...")
#         print(f"Uploading trimmed video: {trimmed_path}")
#         await message.reply_video(
#             trimmed_path, 
#             caption=f"🎬 Random {sample_duration}s sample (starts at {start_time}s)"
#         )
#         print("Upload complete")
        
#     except Exception as e:
#         print(f"Error in processing: {str(e)}")
#         await status_msg.edit(f"❌ Error: {str(e)}")
#     finally:
#         # Clean up
#         print("Cleaning up temporary files")
#         if os.path.exists(path):
#             os.remove(path)
#             print(f"Removed {path}")
#         if os.path.exists(trimmed_path):
#             os.remove(trimmed_path)
#             print(f"Removed {trimmed_path}")
#         if 'clip' in locals():
#             clip.close()
#             print("Closed video clip object")

    


    
        

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
