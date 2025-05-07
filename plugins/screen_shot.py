import os
import time
import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from moviepy import VideoFileClip
from helper.utils import progress_for_pyrogram
from pyrogram.enums import ParseMode


@Client.on_message(filters.private & filters.command("ss"))
async def screenshot_handler(client, message):
    print(f"Command received: {message.command}")
    
    # Step 1: Check usage
    replied = message.reply_to_message
    print(f"Has replied message: {replied is not None}")
    
    if not replied:
        print("No replied message found")
        return await message.reply_text("❌ Error: Please reply to a video message when using this command.")

    elif not (replied.video or replied.document):
        print("Replied message is not a video or document")
        return await message.reply_text("❌ Error: This command only works on actual videos or video documents.")

    elif len(message.command) == 1:
        print("Command used without parameters")
        return await message.reply_text("❌ Error: Format should be /ss (number-of-screenshots).")
    
    # Step 2: Parse and validate screenshot count
    try:
        print(f"Trying to parse screenshot count: {message.command[1]}")
        ss_count = int(message.command[1])
        print(f"Parsed screenshot count: {ss_count}")
        
        if ss_count <= 0:
            print("Screenshot count is not positive")
            return await message.reply("❌ Error: Screenshot count must be a positive number.")
            
        # For practical reasons, limit the number of screenshots
        if ss_count > 10:
            print("Screenshot count too high")
            return await message.reply("❌ Error: Maximum 10 screenshots allowed at once.")
    except ValueError:
        print(f"Failed to parse '{message.command[1]}' as an integer")
        return await message.reply("❌ Error: Screenshot count must be a number.")
    
    # Step 3: Download the video with progress bar
    new_filename = f"video_{message.from_user.id}_{int(time.time())}.mkv"
    file_path = f"downloads/{new_filename}"
    if replied.document:
        file_name_2 = replied.document.file_name or "video.mkv"
    elif replied.video:
        file_name_2 = replied.video.file_name or "video.mkv"
    else:
        file_name_2 = "video.mkv"
    
    # Ensure downloads directory exists
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("downloads/screenshots", exist_ok=True)
    print(f"Downloading to: {file_path}")
    
    # Use progress bar during the download process
    status_msg = await message.reply_text("Trying To Download...", reply_to_message_id=replied.id)
    try:
        path = await client.download_media(
            message=replied,
            file_name=file_path,
            progress=progress_for_pyrogram, 
            progress_args=("**Analyzing Started... **", status_msg, time.time())
        )
        print(f"File downloaded to {path}")
    except Exception as e:
        print(f"Error downloading media: {e}")
        return await status_msg.edit(f"❌ Download error: {str(e)}")
    
    try:
        # Step 4: Analyze video and take screenshots
        print(f"Analyzing video at {path}")
        clip = VideoFileClip(path)
        actual_duration = int(clip.duration)
        print(f"Video duration: {actual_duration}s")
        
        # Step 5: Calculate random timestamps for screenshots
        await status_msg.edit(f"Taking {ss_count} random screenshots...")
        
        # Calculate timestamps for screenshots (random)
        timestamps = []
        # Generate random timestamps, ensuring they are unique
        while len(timestamps) < ss_count:
            # Avoid the first and last 1 second of video
            safe_start = min(1, actual_duration // 10)
            safe_end = max(0, actual_duration - safe_start)
            
            if safe_end <= safe_start:  # Handle very short videos
                safe_end = actual_duration
                safe_start = 0
                
            random_time = random.randint(safe_start, safe_end)
            
            # Ensure we don't have duplicates or very close timestamps
            if all(abs(random_time - t) > 1 for t in timestamps):
                timestamps.append(random_time)
        
        # Sort timestamps for organized viewing
        timestamps.sort()
        
        print(f"Screenshot timestamps: {timestamps}")
        
        # Step 6: Take screenshots and save paths
        screenshot_paths = []
        for i, timestamp in enumerate(timestamps):
            ss_path = f"downloads/screenshots/ss_{message.from_user.id}_{int(time.time())}_{i+1}.jpg"
            frame = clip.get_frame(timestamp)
            
            # Save the frame as an image
            from PIL import Image
            import numpy as np
            img = Image.fromarray(np.uint8(frame))
            img.save(ss_path)
            
            screenshot_paths.append((ss_path, timestamp))
            print(f"Saved screenshot {i+1} at {timestamp}s to {ss_path}")
        
        # Close the clip
        clip.close()
        
        # Step 7: Send screenshots as a media group
        await status_msg.edit("Uploading screenshots...")
        
        # Format time for captions
        def format_timestamp(seconds):
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        
        media_group = []
        for i, (ss_path, timestamp) in enumerate(screenshot_paths):
            media_group.append({
                "type": "photo",
                "media": ss_path,
                "caption": f"Screenshot {i+1}/{ss_count} at {format_timestamp(timestamp)}"
            })
        
        # Send as a media group
        await client.send_media_group(
            chat_id=message.chat.id,
            media=media_group
        )
        
        await status_msg.delete()
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
        
        # Remove screenshot files
        for ss_path, _ in screenshot_paths:
            if os.path.exists(ss_path):
                os.remove(ss_path)
                print(f"Removed {ss_path}")
