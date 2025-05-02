import os
import time
import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from moviepy import VideoFileClip  # Correct import
from helper.utils import progress_for_pyrogram
import re
from datetime import timedelta
from pyrogram.enums import ParseMode


def escape_markdown(text: str) -> str:
    return re.sub(r'([_*\[\]()~`>#+=|{}.!\\-])', r'\\\1', text)

@Client.on_message(filters.private & filters.command("sv"))
async def sample_video_handler(client, message):
    print(f"Command received: {message.command}")
    print(f"Command length: {len(message.command)}")
    
    # Step 1: Check usage
    replied = message.reply_to_message
    print(f"Has replied message: {replied is not None}")
    
    if not replied:
        print("No replied message found")
        return await message.reply_text("❌ Error : Please reply to a video message when using this command.")

    elif not (replied.video or replied.document):
        print("Replied message is not a video or document")
        return await message.reply_text("❌ Error : This command only works on actual videos or video documents.")

    elif len(message.command) == 1:
        print("Command used without parameters")
        try:
            return await message.reply_text("❌ Error : Format should be `/sv (duration-in-seconds)`.", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            print(f"{e}")
    elif len(message.command) > 2:
        print(f"Too many parameters: {message.command[1:]}")
        return await message.reply_text("❌ Error : Format should be `/sv (duration-in-seconds)`.", parse_mode=ParseMode.MARKDOWN)

        
    # Step 3: Parse and validate duration
    try:
        print(f"Trying to parse duration: {message.command[1]}")
        sample_duration = int(message.command[1])
        print(f"Parsed duration: {sample_duration}")
        if sample_duration <= 0:
            print("Duration is not positive")
            return await message.reply("❌ Error : Duration must be a positive number.")
    except ValueError:
        print(f"Failed to parse '{message.command[1]}' as an integer")
        return await message.reply("❌ Error : Duration must be a number.")
        
    # Step 4: Download the video with progress bar
    new_filename = f"video_{message.from_user.id}_{int(time.time())}.mkv"
    file_path = f"downloads/{new_filename}"
    if replied.document:
        file_name_2 = replied.document.file_name or "sample.mkv"
    elif replied.video:
        file_name_2 = replied.video.file_name or "sample.mkv"
    else:
        file_name_2 = "sample.mkv"
    
    # Ensure downloads directory exists
    os.makedirs("downloads", exist_ok=True)
    print(f"Downloading to: {file_path}")
    
    # Use progress bar during the download process
    status_msg = await message.reply_text("Trying to download...")
    try:
        path = await client.download_media(
            message=replied,
            file_name=file_path,
            progress=progress_for_pyrogram, 
            progress_args=("**Download Started... **", status_msg, time.time())
        )
        print(f"File downloaded to {path}")
    except Exception as e:
        print(f"Error downloading media: {e}")
        return await status_msg.edit(f"❌ Download error: {str(e)}")
        
    try:
        # Step 5: Check video duration
        print(f"Analyzing video at {path}")
        clip = VideoFileClip(path)
        actual_duration = int(clip.duration)
        print(f"Video duration: {actual_duration}s")
        
        if sample_duration > actual_duration:
            print(f"Requested duration ({sample_duration}s) exceeds video length ({actual_duration}s)")
            clip.close()
            os.remove(path)
            return await status_msg.edit(f"❌ Error : Given duration ({sample_duration}s) is longer than the actual video duration ({actual_duration}s).")
            
        # Step 6: Choose random start time
        max_start = actual_duration - sample_duration
        start_time = random.randint(0, max_start)
        formatted_time = str(timedelta(seconds=start_time))
        trimmed_path = f"downloads/sample_{message.from_user.id}_{int(time.time())}_{sample_duration}s.mkv"
        print(f"Selected segment: {start_time}s to {start_time + sample_duration}s")
        print(f"Output will be saved to: {trimmed_path}")
        
        await status_msg.edit(f"Trimming Random {sample_duration}s segment from {formatted_time}s...")
        
        # Use ffmpeg to extract the segment
        cmd = f'ffmpeg -ss {start_time} -i "{path}" -t {sample_duration} -c copy "{trimmed_path}" -y'
        print(f"Running command: {cmd}")
        process = await asyncio.create_subprocess_shell(cmd)
        await process.communicate()
        print("FFmpeg processing complete")
        
        # Step 7: Send trimmed video
        await status_msg.edit("📤 Uploading sample video...")
        print(f"Uploading trimmed video: {trimmed_path}")
        await message.reply_video(
            trimmed_path, 
            caption=f"<b>{sample_duration}s Sample (starts at {formatted_time}s)</b> of <u>{file_name_2}</u>",
            parse_mode=ParseMode.HTML
        )
        print("Upload complete")
        
    except Exception as e:
        print(f"Error in processing: {str(e)}")
        await status_msg.edit(f"❌ Error: {str(e)}")
    finally:
        # Clean up
        print("Cleaning up temporary files")
        if os.path.exists(path):
            os.remove(path)
            print(f"Removed {path}")
        if os.path.exists(trimmed_path):
            os.remove(trimmed_path)
            print(f"Removed {trimmed_path}")
        if 'clip' in locals():
            clip.close()
            print("Closed video clip object")
