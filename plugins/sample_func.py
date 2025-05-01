import random
import asyncio
import os
import time
import shutil
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

@Client.on_message(filters.private & filters.command("sv"))
async def sample_video_handler(client, message):
    print(f"Command received: {message.command}")
    
    # Step 1: Check usage
    replied = message.reply_to_message
    print(f"Has replied message: {replied is not None}")
    
    if not replied:
        return await message.reply("❌ Please reply to a video message when using this command.")
    
    # Check if duration is provided
    if len(message.command) == 1:  # Only "/sv" without any parameter
        sample_duration = 10  # Default to 10 seconds if not provided
        print("Using default 10 second duration")
    else:
        # Parse and validate duration
        try:
            print(f"Trying to parse duration: {message.command[1]}")
            sample_duration = int(message.command[1])
            print(f"Parsed duration: {sample_duration}")
            if sample_duration <= 0:
                return await message.reply("❌ Duration must be a positive number.")
        except ValueError:
            print(f"Failed to parse '{message.command[1]}' as an integer")
            return await message.reply("❌ Duration must be a number.")
    
    # Step 2: Validate replied message
    print(f"Replied message type - video: {replied.video is not None}, document: {replied.document is not None}")
    if not (replied.video or replied.document):
        print("Replied message is not a video or document")
        return await message.reply("❌ This command only works on actual videos or video documents.")
    
    # Step 3: Get video file ID and information
    if replied.video:
        file_id = replied.video.file_id
        actual_duration = replied.video.duration
    else:  # Document
        if not replied.document.mime_type or not replied.document.mime_type.startswith("video/"):
            return await message.reply("❌ This document doesn't appear to be a video.")
        file_id = replied.document.file_id
        # We don't know document duration, so we'll need to estimate or handle specially
        actual_duration = None
        
    status_msg = await message.reply_text("Processing video...")
    
    try:
        # Step 4: Get file info to determine where to start
        file_info = await client.get_file(file_id)
        file_url = file_info.download_url if hasattr(file_info, 'download_url') else None
        
        if not file_url and not hasattr(file_info, 'file_path'):
            # Fall back to older method if we can't get direct URLs
            return await old_method_full_download(client, message, replied, sample_duration, status_msg)
        
        # Step 5: Determine random segment if we have duration info
        if actual_duration:
            if sample_duration > actual_duration:
                return await status_msg.edit(f"❌ Given duration ({sample_duration}s) is longer than the actual video duration ({actual_duration}s).")
                
            # Choose random start time
            max_start = actual_duration - sample_duration
            start_time = random.randint(0, max_start)
        else:
            # For documents where we don't have duration, we'll just start from the beginning
            # Or you could first probe the file to get its duration
            start_time = 0
            
        print(f"Selected segment: {start_time}s to {start_time + sample_duration}s")
        
        # Step 6: Set up output paths
        output_filename = f"sample_{message.from_user.id}_{int(time.time())}_{sample_duration}s.mp4"
        output_path = f"downloads/{output_filename}"
        os.makedirs("downloads", exist_ok=True)
        
        await status_msg.edit(f"📥 Extracting {sample_duration}s segment from {start_time}s...")
        
        # Step 7: Direct download of segment using FFmpeg
        if file_url:
            # If we have a direct URL, we can use FFmpeg to directly extract the segment
            cmd = f'ffmpeg -ss {start_time} -i "{file_url}" -t {sample_duration} -c copy "{output_path}" -y'
        else:
            # Otherwise use Pyrogram's file path
            file_path = file_info.file_path
            cmd = f'ffmpeg -ss {start_time} -i "{file_path}" -t {sample_duration} -c copy "{output_path}" -y'
            
        print(f"Running command: {cmd}")
        process = await asyncio.create_subprocess_shell(cmd)
        await process.communicate()
        print("FFmpeg processing complete")
        
        # Step 8: Send trimmed video
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            print("Output file is missing or empty, falling back to full download method")
            return await old_method_full_download(client, message, replied, sample_duration, status_msg)
            
        await status_msg.edit("📤 Uploading sample video...")
        print(f"Uploading trimmed video: {output_path}")
        await message.reply_video(
            output_path, 
            caption=f"🎬 Random {sample_duration}s sample (starts at {start_time}s)"
        )
        print("Upload complete")
        
    except Exception as e:
        print(f"Error in processing: {str(e)}")
        await status_msg.edit(f"❌ Error: {str(e)}")
        # Fall back to old method if new method fails
        try:
            return await old_method_full_download(client, message, replied, sample_duration, status_msg)
        except Exception as e2:
            print(f"Fallback method also failed: {str(e2)}")
            await status_msg.edit(f"❌ All extraction methods failed. Error: {str(e)}")
    finally:
        # Clean up
        if 'output_path' in locals() and os.path.exists(output_path):
            os.remove(output_path)
            print(f"Removed {output_path}")

# Fallback function that uses the original method of downloading the entire file first
async def old_method_full_download(client, message, replied, sample_duration, status_msg=None):
    if not status_msg:
        status_msg = await message.reply_text("Falling back to full download method...")
    else:
        await status_msg.edit("⚠️ Direct extraction failed. Falling back to full download method...")
    
    # Full download process - this is your original method
    new_filename = f"video_{message.from_user.id}_{int(time.time())}.mp4"
    file_path = f"downloads/{new_filename}"
    
    # Ensure downloads directory exists
    os.makedirs("downloads", exist_ok=True)
    print(f"Downloading full video to: {file_path}")
    
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
        raise e
        
    try:
        # Check video duration
        print(f"Analyzing video at {path}")
        clip = VideoFileClip(path)
        actual_duration = int(clip.duration)
        print(f"Video duration: {actual_duration}s")
        
        if sample_duration > actual_duration:
            print(f"Requested duration ({sample_duration}s) exceeds video length ({actual_duration}s)")
            clip.close()
            os.remove(path)
            return await status_msg.edit(f"❌ Given duration ({sample_duration}s) is longer than the actual video duration ({actual_duration}s).")
            
        # Choose random start time
        max_start = actual_duration - sample_duration
        start_time = random.randint(0, max_start)
        trimmed_path = f"downloads/sample_{message.from_user.id}_{int(time.time())}_{sample_duration}s.mp4"
        print(f"Selected segment: {start_time}s to {start_time + sample_duration}s")
        print(f"Output will be saved to: {trimmed_path}")
        
        await status_msg.edit(f"✂️ Trimming random {sample_duration}s segment from {start_time}s...")
        
        # Use ffmpeg to extract the segment
        cmd = f'ffmpeg -ss {start_time} -i "{path}" -t {sample_duration} -c copy "{trimmed_path}" -y'
        print(f"Running command: {cmd}")
        process = await asyncio.create_subprocess_shell(cmd)
        await process.communicate()
        print("FFmpeg processing complete")
        
        # Send trimmed video
        await status_msg.edit("📤 Uploading sample video...")
        print(f"Uploading trimmed video: {trimmed_path}")
        await message.reply_video(
            trimmed_path, 
            caption=f"🎬 Random {sample_duration}s sample (starts at {start_time}s)"
        )
        print("Upload complete")
        return True
        
    except Exception as e:
        print(f"Error in processing: {str(e)}")
        raise e
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
