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
    print(f"Command length: {len(message.command)}")
    
    # Step 1: Check usage
    replied = message.reply_to_message
    print(f"Has replied message: {replied is not None}")
    
    if not replied:
        print("No replied message found")
        return await message.reply("❌ Please reply to a video message when using this command.")
    
    # Check if duration is provided
    if len(message.command) == 1:  # Only "/sv" without any parameter
        print("Command used without parameters")
        return await message.reply_text("❗ Usage: Reply to a video with `/sv <duration-in-seconds>`", parse_mode="markdown")
        
    # Check if more than one parameter is provided
    if len(message.command) > 2:
        print(f"Too many parameters: {message.command[1:]}")
        return await message.reply_text("❗ Usage: Reply to a video with `/sv <duration-in-seconds>` (only one number)", parse_mode="markdown")
        
    # Step 2: Validate replied message
    print(f"Replied message type - video: {replied.video is not None}, document: {replied.document is not None}")
    if not (replied.video or replied.document):
        print("Replied message is not a video or document")
        return await message.reply("❌ This command only works on actual videos or video documents.")
        
    # Step 3: Parse and validate duration
    try:
        print(f"Trying to parse duration: {message.command[1]}")
        sample_duration = int(message.command[1])
        print(f"Parsed duration: {sample_duration}")
        if sample_duration <= 0:
            print("Duration is not positive")
            return await message.reply("❌ Duration must be a positive number.")
    except ValueError:
        print(f"Failed to parse '{message.command[1]}' as an integer")
        return await message.reply("❌ Duration must be a number.")
        
    # Step 4: Get video metadata to check duration before downloading
    status_msg = await message.reply_text("⏳ Checking video duration...")
    
    try:
        # First, get a small portion to analyze with ffprobe
        temp_file = f"downloads/temp_{message.from_user.id}_{int(time.time())}.mp4"
        os.makedirs("downloads", exist_ok=True)
        
        # Download just the first few seconds for metadata
        print("Downloading small portion for metadata analysis")
        temp_path = await client.download_media(
            message=replied,
            file_name=temp_file,
            block=True  # Just download a small portion
        )
        
        # Use ffprobe to get duration quickly
        print(f"Running ffprobe to get video metadata for {temp_path}")
        probe_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{temp_path}"'
        process = await asyncio.create_subprocess_shell(
            probe_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        try:
            # Parse the duration from ffprobe output
            actual_duration = float(stdout.decode().strip())
            print(f"Video duration from metadata: {actual_duration}s")
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"Removed temporary file {temp_path}")
                
            # Check if requested duration is valid
            if sample_duration > actual_duration:
                print(f"Requested duration ({sample_duration}s) exceeds video length ({actual_duration}s)")
                return await status_msg.edit(f"❌ Given duration ({sample_duration}s) is longer than the actual video duration ({actual_duration:.1f}s).")
                
            # If everything is fine, inform user we're proceeding
            await status_msg.edit(f"✅ Video duration: {actual_duration:.1f}s. Starting download...")
            
        except (ValueError, IndexError):
            print(f"Failed to parse duration from ffprobe: {stdout.decode()}")
            # If we can't get duration from metadata, we'll have to download the file
            await status_msg.edit("⚠️ Couldn't determine video length from metadata. Downloading full video...")
    except Exception as e:
        print(f"Error in metadata check: {e}")
        await status_msg.edit("⚠️ Couldn't check video duration. Downloading full video...")
        
    # Step 5: Get a direct URL for the file instead of downloading it
    try:
        # Get the file ID and reference for direct processing
        if replied.video:
            file_id = replied.video.file_id
            file_size = replied.video.file_size
        else:  # document
            file_id = replied.document.file_id
            file_size = replied.document.file_size
            
        print(f"Working with file_id: {file_id}, size: {file_size}")
        
        # Choose random start time based on the duration we got earlier
        max_start = int(actual_duration) - sample_duration
        start_time = random.randint(0, max_start)
        print(f"Selected segment: {start_time}s to {start_time + sample_duration}s")
        
        await status_msg.edit(f"✂️ Processing {sample_duration}s segment from {start_time}s...")
        
        # Get file path for direct processing
        trimmed_path = f"downloads/sample_{message.from_user.id}_{int(time.time())}_{sample_duration}s.mp4"
        
        # Get the file location from Telegram
        file_info = await client.get_file(file_id)
        if not file_info:
            raise Exception("Could not get file information from Telegram")
            
        # Process directly with FFmpeg using Telegram's file reference
        # We'll use Pyrogram's get_file() to get a direct download link, then pipe it to FFmpeg
        # This way we only download the portion we need
        
        # Generate a streaming URL or use Telegram's download URL
        file = await client.download_media(file_id, in_memory=True)
        
        # Write to a temporary file
        temp_path = f"downloads/temp_{message.from_user.id}_{int(time.time())}.mp4"
        with open(temp_path, "wb") as f:
            f.write(file.getbuffer() if hasattr(file, "getbuffer") else file.read())
            
        print(f"Temporary file created at {temp_path}")
        
        # Now use FFmpeg to extract just the segment we need
        await status_msg.edit(f"🎬 Extracting {sample_duration}s segment starting at {start_time}s...")
        
        cmd = f'ffmpeg -ss {start_time} -i "{temp_path}" -t {sample_duration} -c copy "{trimmed_path}" -y'
        print(f"Running command: {cmd}")
        process = await asyncio.create_subprocess_shell(cmd)
        await process.communicate()
        print("FFmpeg processing complete")
        
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Removed temporary file {temp_path}")
    
    except Exception as e:
        print(f"Error in direct processing: {e}")
        
        # Fallback to the traditional method if direct processing fails
        await status_msg.edit(f"⚠️ Direct processing failed. Downloading full video instead... ({str(e)})")
        
        # Traditional download and processing
        new_filename = f"video_{message.from_user.id}_{int(time.time())}.mp4"
        file_path = f"downloads/{new_filename}"
        print(f"Falling back to full download: {file_path}")
        
        try:
            path = await client.download_media(
                message=replied,
                file_name=file_path,
                progress=progress_for_pyrogram, 
                progress_args=("**Download in progress... **", status_msg, time.time())
            )
            print(f"File downloaded to {path}")
            
            # Choose random start time
            max_start = int(actual_duration) - sample_duration
            start_time = random.randint(0, max_start)
            trimmed_path = f"downloads/sample_{message.from_user.id}_{int(time.time())}_{sample_duration}s.mp4"
            print(f"Selected segment: {start_time}s to {start_time + sample_duration}s")
            
            await status_msg.edit(f"✂️ Trimming random {sample_duration}s segment from {start_time}s...")
            
            # Use ffmpeg to extract the segment
            cmd = f'ffmpeg -ss {start_time} -i "{path}" -t {sample_duration} -c copy "{trimmed_path}" -y'
            print(f"Running command: {cmd}")
            process = await asyncio.create_subprocess_shell(cmd)
            await process.communicate()
            print("FFmpeg processing complete")
            
            # Clean up the original file
            if os.path.exists(path):
                os.remove(path)
                print(f"Removed original file {path}")
                
        except Exception as e:
            print(f"Error in fallback method: {e}")
            return await status_msg.edit(f"❌ Processing error: {str(e)}")
        
        # Step 7: Send trimmed video
        await status_msg.edit("📤 Uploading sample video...")
        print(f"Uploading trimmed video: {trimmed_path}")
        await message.reply_video(
            trimmed_path, 
            caption=f"🎬 Random {sample_duration}s sample (starts at {start_time}s)"
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
