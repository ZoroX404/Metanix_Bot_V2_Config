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
    print(f"Command received: {message.command}")
    
    # Step 1: Check usage
    replied = message.reply_to_message
    
    if not replied:
        return await message.reply("❌ Please reply to a video message when using this command.")
    
    # Check if duration is provided
    if len(message.command) == 1:  # Only "/sv" without any parameter
        return await message.reply_text("❗ Usage: Reply to a video with `/sv <duration-in-seconds>`", parse_mode="markdown")
        
    # Check if more than one parameter is provided
    if len(message.command) > 2:
        return await message.reply_text("❗ Usage: Reply to a video with `/sv <duration-in-seconds>` (only one number)", parse_mode="markdown")
        
    # Step 2: Validate replied message
    if not (replied.video or replied.document):
        return await message.reply("❌ This command only works on actual videos or video documents.")
        
    # Step 3: Parse and validate duration
    try:
        sample_duration = int(message.command[1])
        if sample_duration <= 0:
            return await message.reply("❌ Duration must be a positive number.")
    except ValueError:
        return await message.reply("❌ Duration must be a number.")
        
    # Step 4: Initialize status message
    status_msg = await message.reply_text("⏳ Analyzing video...")
    
    try:
        # Get file info for direct access
        if replied.video:
            file_id = replied.video.file_id
        else:  # document
            file_id = replied.document.file_id
            
        # Get the file location without downloading
        file_info = await client.get_file(file_id)
        file_path = file_info.file_path
        
        # Use ffprobe to get duration without downloading the whole file
        # This works directly with the Telegram file path
        probe_cmd = f'ffprobe -v error -select_streams v:0 -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 tg://{file_path}'
        
        process = await asyncio.create_subprocess_shell(
            probe_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        # Parse the duration
        try:
            actual_duration = float(stdout.decode().strip())
            print(f"Video duration: {actual_duration}s")
            
            if sample_duration > actual_duration:
                return await status_msg.edit(f"❌ Given duration ({sample_duration}s) is longer than the actual video duration ({actual_duration:.1f}s).")
                
        except (ValueError, IndexError):
            await status_msg.edit("⚠️ Couldn't determine video duration. Processing anyway...")
            # Set a default large value
            actual_duration = 3600  # Assume it's an hour long if we can't determine
        
        # Choose random start time
        max_start = int(actual_duration) - sample_duration
        if max_start < 0:
            max_start = 0
        start_time = random.randint(0, max_start)
        
        await status_msg.edit(f"✂️ Extracting {sample_duration}s segment from position {start_time}s...")
        
        # Create output path
        os.makedirs("downloads", exist_ok=True)
        output_path = f"downloads/sample_{message.from_user.id}_{int(time.time())}_{sample_duration}s.mp4"
        
        # *** KEY OPTIMIZATION: Stream directly from Telegram API and extract only the needed segment ***
        # Use FFmpeg's ability to read from stdin and seek efficiently
        
        # Command to stream from Telegram and extract segment in one step
        # This uses HTTP byte range requests under the hood when available
        cmd = (
            f'ffmpeg -ss {start_time} -i tg://{file_path} '
            f'-t {sample_duration} -c:v copy -c:a copy -avoid_negative_ts 1 '
            f'-movflags +faststart "{output_path}" -y'
        )
        
        print(f"Running optimized command: {cmd}")
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        # Check if the file was created successfully
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            print("Failed with direct streaming method. Stderr:")
            print(stderr.decode())
            
            # Fallback: Download small segment first, then process
            await status_msg.edit("⚠️ Direct processing failed. Using alternative method...")
            
            # Get file location for byte range request
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            
            # Calculate byte ranges for the segment we need
            # This is an approximation - we'll request a bit more than needed to ensure we get our segment
            bytes_per_second = 1_000_000  # Rough estimate - 1MB per second
            start_byte = max(0, int((start_time - 5) * bytes_per_second))  # Start 5 seconds earlier to be safe
            end_byte = int((start_time + sample_duration + 5) * bytes_per_second)  # End 5 seconds later to be safe
            
            # Create temp file for the segment
            temp_path = f"downloads/temp_{message.from_user.id}_{int(time.time())}.mp4"
            
            # Download just the byte range we need
            await status_msg.edit(f"📥 Downloading only the needed segment...")
            
            async with aiohttp.ClientSession() as session:
                headers = {"Range": f"bytes={start_byte}-{end_byte}"}
                async with session.get(file_url, headers=headers) as response:
                    if response.status == 206:  # Partial Content
                        with open(temp_path, 'wb') as f:
                            while True:
                                chunk = await response.content.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                    else:
                        raise Exception(f"Failed to get byte range: HTTP {response.status}")
            
            # Now process the temp file
            cmd = (
                f'ffmpeg -ss 5 -i "{temp_path}" '  # 5 second offset since we started 5 seconds early
                f'-t {sample_duration} -c:v copy -c:a copy '
                f'-movflags +faststart "{output_path}" -y'
            )
            
            print(f"Running fallback command: {cmd}")
            process = await asyncio.create_subprocess_shell(cmd)
            await process.communicate()
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        # Send the trimmed video
        await status_msg.edit("📤 Uploading sample video...")
        await message.reply_video(
            output_path, 
            caption=f"🎬 Random {sample_duration}s sample (starts at {start_time}s)"
        )
        
        # Clean up
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        print(f"Error in processing: {str(e)}")
        await status_msg.edit(f"❌ Error: {str(e)}")
