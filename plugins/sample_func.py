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
    
    if not replied:
        return await message.reply("❌ Please reply to a video message when using this command.")
    
    # Check if duration is provided
    if len(message.command) == 1:  # Only "/sv" without any parameter
        return await message.reply_text("❗ Usage: Reply to a video with /sv <duration-in-seconds>", parse_mode="markdown")
        
    # Check if more than one parameter is provided
    if len(message.command) > 2:
        return await message.reply_text("❗ Usage: Reply to a video with /sv <duration-in-seconds> (only one number)", parse_mode="markdown")
        
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
        # Create download directory if it doesn't exist
        os.makedirs("downloads", exist_ok=True)
        
        # First download a small portion to analyze the duration
        temp_file = f"downloads/temp_{message.from_user.id}_{int(time.time())}.mp4"
        
        # Get information
        if replied.video:
            video_duration = replied.video.duration  # Pyrogram provides duration for videos
            file_id = replied.video.file_id
        else:  # document
            video_duration = None  # Unknown for documents
            file_id = replied.document.file_id
        
        # If we don't have duration from metadata, we'll need to download and check
        if video_duration is None:
            await status_msg.edit("📥 Downloading a small portion to analyze...")
            
            # Download just the first few seconds to check duration
            await client.download_media(
                message=replied,
                file_name=temp_file,
                block=True,  # Important: block until download completes
                limit=5 * 1024 * 1024  # Limit to ~5MB
            )
            
            # Use ffprobe to get the duration
            probe_cmd = f'ffprobe -v error -select_streams v:0 -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{temp_file}"'
            
            process = await asyncio.create_subprocess_shell(
                probe_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            try:
                video_duration = float(stdout.decode().strip())
                print(f"Video duration (from ffprobe): {video_duration}s")
            except (ValueError, IndexError):
                await status_msg.edit("⚠️ Couldn't determine video duration. Using default value...")
                video_duration = 3600  # Assume it's an hour long if we can't determine
        
        # Check if requested duration fits within the video
        if sample_duration > video_duration:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return await status_msg.edit(f"❌ Given duration ({sample_duration}s) is longer than the actual video duration ({video_duration:.1f}s).")
        
        # Choose random start time
        max_start = int(video_duration) - sample_duration
        if max_start < 0:
            max_start = 0
        start_time = random.randint(0, max_start)
        
        await status_msg.edit(f"✂️ Extracting {sample_duration}s segment from position {start_time}s...")
        
        # Define output path
        output_path = f"downloads/sample_{message.from_user.id}_{int(time.time())}_{sample_duration}s.mp4"
        
        # Method 1: If we already have the temp file, extract from it
        if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
            # Check if temp file contains our desired segment
            if start_time < 5:  # If the segment starts within the first 5 seconds
                cmd = (
                    f'ffmpeg -ss {start_time} -i "{temp_file}" '
                    f'-t {sample_duration} -c:v copy -c:a copy '
                    f'-movflags +faststart "{output_path}" -y'
                )
                
                print(f"Extracting from temp file: {cmd}")
                process = await asyncio.create_subprocess_shell(cmd)
                await process.communicate()
                
                # If extraction was successful, we're done
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    os.remove(temp_file)
                    goto_upload = True
                else:
                    # If extraction failed, we'll try the direct download method below
                    goto_upload = False
            else:
                # Start time is beyond our temp file, we need to use another approach
                os.remove(temp_file)
                goto_upload = False
        else:
            goto_upload = False
        
        # Method 2: Direct full extraction with pyrogram
        if not goto_upload:
            await status_msg.edit(f"📥 Downloading and processing segment...")
            
            # Download the entire file
            downloaded_file = await client.download_media(
                message=replied,
                file_name=temp_file
            )
            
            cmd = (
                f'ffmpeg -ss {start_time} -i "{downloaded_file}" '
                f'-t {sample_duration} -c:v copy -c:a copy '
                f'-movflags +faststart "{output_path}" -y'
            )
            
            print(f"Extracting from full download: {cmd}")
            process = await asyncio.create_subprocess_shell(cmd)
            await process.communicate()
            
            # Clean up the downloaded file
            if os.path.exists(downloaded_file):
                os.remove(downloaded_file)
        
        # Check if output file was created successfully
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise Exception("Failed to create sample video file")
        
        # Upload the sample
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
        await status_msg.edit(f"❌ An error occurred: {str(e)}")
