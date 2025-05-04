
# import os
# import time
# import random
# import asyncio
# from pyrogram import Client, filters
# from pyrogram.types import Message
# from moviepy import VideoFileClip  # Correct import
# from helper.utils import progress_for_pyrogram
# import re
# from datetime import timedelta
# from pyrogram.enums import ParseMode


# def escape_markdown(text: str) -> str:
#     return re.sub(r'([_*\[\]()~`>#+=|{}.!\\-])', r'\\\1', text)

# from datetime import datetime

# def parse_time(t: str) -> int:
#     """Convert HH:MM:SS or seconds string to integer seconds."""
#     try:
#         if ":" in t:
#             x = datetime.strptime(t, "%H:%M:%S")
#             return x.hour * 3600 + x.minute * 60 + x.second
#         return int(t)
#     except ValueError:
#         return -1

# @Client.on_message(filters.private & filters.command("trim"))
# async def trim_video_handler(client, message):
#     replied = message.reply_to_message

#     if not replied:
#         return await message.reply_text("❌ Please reply to a video message.")

#     if not (replied.video or replied.document):
#         return await message.reply_text("❌ Only works on video or video document messages.")

#     if len(message.command) != 3:
#         return await message.reply_text("❌ Usage: /trim start end\n**Example:** `/trim 01:45:06 01:45:56` or `/trim 400 500`", parse_mode=ParseMode.MARKDOWN)

#     # Parse time range
#     start_input, end_input = message.command[1], message.command[2]
#     start_time = parse_time(start_input)
#     end_time = parse_time(end_input)

#     if start_time < 0 or end_time < 0:
#         return await message.reply_text("❌ Invalid time format.\n**Example:** `/trim 01:45:06 01:45:56` or `/trim 400 500`.", parse_mode=ParseMode.MARKDOWN)

#     if start_time >= end_time:
#         return await message.reply_text("❌ End time must be greater than start time.")

#     duration = end_time - start_time

#     # Download logic remains unchanged...
#     new_filename = f"video_{message.from_user.id}_{int(time.time())}.mkv"
#     file_path = f"downloads/{new_filename}"
#     file_name_2 = (replied.document.file_name if replied.document else replied.video.file_name) or "sample.mkv"
#     os.makedirs("downloads", exist_ok=True)

#     status_msg = await message.reply_text("Trying To Download.....", reply_to_message_id=replied.id)
#     try:
#         path = await client.download_media(
#             message=replied,
#             file_name=file_path,
#             progress=progress_for_pyrogram, 
#             progress_args=("**Analyzing Started... **", status_msg, time.time())
#         )
#     except Exception as e:
#         return await status_msg.edit(f"❌ Download error: {str(e)}")

#     try:
#         clip = VideoFileClip(path)
#         actual_duration = int(clip.duration)
#         clip.close()

#         if end_time > actual_duration:
#             os.remove(path)
#             return await status_msg.edit(f"❌ End time exceeds video duration ({actual_duration}s).")

#         trimmed_path = f"downloads/sample_{message.from_user.id}_{int(time.time())}_{duration}s.mkv"
#         await status_msg.edit(f"Trimming {duration}s from {start_input} to {end_input}...")

#         # Use ffmpeg to trim
#         cmd = f'ffmpeg -ss {start_time} -i "{path}" -t {duration} -c copy "{trimmed_path}" -y'
#         process = await asyncio.create_subprocess_shell(cmd)
#         await process.communicate()

#         if ":" not in message.command[1]:
#             start_input = str(timedelta(seconds=start_time))
#         if ":" not in message.command[2]:
#             end_input = str(timedelta(seconds=end_time))
    
        
#         await status_msg.edit("Uploading trimmed video...")
#         await message.reply_video(
#             trimmed_path, 
#             caption=f"<b>Trimmed from {start_input} to {end_input}</b> of <u>{file_name_2}</u>",
#             parse_mode=ParseMode.HTML
#         )
#         await status_msg.delete()

#     except Exception as e:
#         await status_msg.edit(f"❌ Error: {str(e)}")
#     finally:
#         if os.path.exists(path):
#             os.remove(path)
#         if os.path.exists(trimmed_path):
#             os.remove(trimmed_path)

