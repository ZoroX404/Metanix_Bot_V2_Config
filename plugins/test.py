#!/usr/bin/env python3
"""
Standalone Telegram Media Info Bot

This script implements a Telegram bot that extracts media information from files
without downloading the entire content. It includes debugging print statements
and comprehensive error handling.

Prerequisites:
- ffprobe (part of ffmpeg)
- mediainfo
- Python 3.7+
- Pyrogram library
"""
from config import Config
import os
import io
import json
import time
import asyncio
import logging
import datetime
import tempfile
from urllib.parse import urlparse
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait

# Configure logging for better debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration - EDIT THESE VALUES
API_ID = Config.API_ID   # Replace with your API ID
API_HASH = Config.API_HASH # Replace with your API hash
BOT_TOKEN = Config.BOT_TOKEN   # Replace with your bot token

# Message templates
class Messages:
    START = "Send me a media file or reply to a media message with /mediainfo to get detailed information about it."
    PROCESSING_REQUEST = "Processing your request..."
    MEDIAINFO_START = "Extracting media information... This won't download the entire file."
    PROCESS_UPLOAD_CONFIRM = "Media info extracted in {total_process_duration}!"
    PROCESS_TIMEOUT = "The process timed out. Please try again."
    UNSUPPORTED_MEDIA = "This doesn't appear to be a media file I can analyze."
    HELP_TEXT = """
**Media Info Bot Help**

This bot extracts detailed information about media files efficiently.

**Commands:**
• /start - Start the bot
• /help - Show this help message
• /mediainfo - Reply to a media file with this command

**Usage:**
1. Send a media file to the bot
2. Reply to it with /mediainfo
3. Or, reply to any media file in any chat with /mediainfo and tag the bot (@yourbotusername)
    """

# Create the Pyrogram client
app = Client(
    "media_info_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Utility class for media info extraction
class MediaInfoUtility:
    @staticmethod
    async def get_media_info(file_path_or_link):
        """
        Extract media information efficiently without downloading the entire file.
        Works with both local files and remote URLs.
        
        Args:
            file_path_or_link: Path to local file or URL
            
        Returns:
            bytes: Media information as JSON bytes
        """
        print(f"Getting media info for: {file_path_or_link}")
        start_time = time.time()
        
        is_url = urlparse(file_path_or_link).scheme in ('http', 'https')
        temp_path = None
        
        try:
            if is_url:
                # For URLs, download only a portion of the file
                print("File is a URL, downloading headers only...")
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_path = temp_file.name
                
                # Use range requests to download just enough data for analysis
                headers = {'Range': 'bytes=0-4194304'}  # First 4MB should be enough for most headers
                
                try:
                    async with aiohttp.ClientSession() as session:
                        print("Making range request...")
                        async with session.get(file_path_or_link, headers=headers) as response:
                            print(f"Response status: {response.status}")
                            if response.status not in (200, 206):
                                print(f"Error: HTTP {response.status}")
                                raise Exception(f"HTTP error: {response.status}")
                            
                            # Save the partial content to a temporary file
                            with open(temp_path, 'wb') as f:
                                chunk = await response.content.read(1024)
                                total_size = 0
                                while chunk:
                                    total_size += len(chunk)
                                    f.write(chunk)
                                    chunk = await response.content.read(1024)
                                print(f"Downloaded {total_size} bytes to {temp_path}")
                
                except Exception as e:
                    print(f"Download error: {e}")
                    if temp_path and os.path.exists(temp_path):
                        os.unlink(temp_path)
                    raise Exception(f"Failed to download file: {e}")
                
                file_path = temp_path
            else:
                # Local file
                file_path = file_path_or_link
                print(f"Using local file: {file_path}")
            
            # First try with ffprobe - works well with partial files
            print("Running ffprobe...")
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]
            
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                stderr_text = stderr.decode() if stderr else ""
                
                if process.returncode != 0:
                    print(f"ffprobe failed with code {process.returncode}")
                    print(f"Error: {stderr_text}")
                    
                    # Try mediainfo as a fallback if ffprobe fails
                    print("Trying mediainfo as fallback...")
                    mediainfo_cmd = [
                        'mediainfo',
                        '--Output=JSON',
                        file_path
                    ]
                    
                    mi_process = await asyncio.create_subprocess_exec(
                        *mediainfo_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    mi_stdout, mi_stderr = await mi_process.communicate()
                    mi_stderr_text = mi_stderr.decode() if mi_stderr else ""
                    
                    if mi_process.returncode == 0:
                        print("mediainfo succeeded!")
                        # Try to validate and pretty-print the JSON
                        try:
                            parsed = json.loads(mi_stdout)
                            result = json.dumps(parsed, indent=2).encode('utf-8')
                            print(f"Extraction took {time.time() - start_time:.2f} seconds")
                            return result
                        except json.JSONDecodeError:
                            print("Invalid JSON from mediainfo")
                            return mi_stdout  # Return raw output if we can't parse it
                    else:
                        print(f"mediainfo also failed: {mi_stderr_text}")
                        raise Exception(f"Both ffprobe and mediainfo failed. Error: {mi_stderr_text}")
                
                # Process ffprobe output
                try:
                    print("ffprobe succeeded, processing output...")
                    parsed = json.loads(stdout)
                    
                    # Add extraction metadata
                    parsed["_extraction_info"] = {
                        "method": "ffprobe",
                        "extraction_time": datetime.datetime.now().isoformat(),
                        "elapsed_seconds": time.time() - start_time
                    }
                    
                    result = json.dumps(parsed, indent=2).encode('utf-8')
                    print(f"Extraction took {time.time() - start_time:.2f} seconds")
                    return result
                    
                except json.JSONDecodeError:
                    print("Invalid JSON from ffprobe")
                    # Return the raw output if we can't parse it
                    return stdout
                
            except Exception as e:
                print(f"Error running media info tools: {e}")
                raise Exception(f"Media info extraction failed: {e}")
                
        finally:
            # Clean up temporary file if it exists
            if temp_path and os.path.exists(temp_path):
                print(f"Cleaning up temp file: {temp_path}")
                os.unlink(temp_path)

# Command handlers
# @app.on_message(filters.command("start"))
# async def start_command(client, message):
#     print(f"Start command from user {message.from_user.id}")
#     await message.reply_text(Messages.START)

# @app.on_message(filters.command("help"))
# async def help_command(client, message):
#     print(f"Help command from user {message.from_user.id}")
#     await message.reply_text(Messages.HELP_TEXT)

@Client.on_message(filters.command("mediainfo") & filters.reply)
async def mediainfo_command(client, message: Message):
    """
    Process /mediainfo command when replying to a message
    """
    user_id = message.from_user.id
    print(f"Media info request from user {user_id}")
    
    reply = message.reply_to_message
    if not reply:
        print("No reply message found")
        await message.reply_text("Please reply to a media message.")
        return
    
    # Check if the replied message contains media
    media_types = ['audio', 'document', 'video', 'animation']
    media_object = None
    file_id = None
    
    for media_type in media_types:
        if hasattr(reply, media_type) and getattr(reply, media_type):
            media_object = getattr(reply, media_type)
            file_id = media_object.file_id
            print(f"Found media type: {media_type}, file_id: {file_id}")
            break
    
    if not file_id:
        print("No media found in the replied message")
        await message.reply_text(Messages.UNSUPPORTED_MEDIA)
        return
    
    # Send processing message
    progress_msg = await message.reply_text(Messages.PROCESSING_REQUEST)
    start_time = time.time()
    
    try:
        print("Getting file link...")
        try:
            file_link = await client.get_file_link(file_id)
            print(f"File link obtained: {file_link}")
        except Exception as e:
            print(f"Error getting file link: {e}")
            await progress_msg.edit_text(f"Error getting file link: {e}")
            return
        
        # Update status
        await progress_msg.edit_text(Messages.MEDIAINFO_START)
        
        # Extract media info
        try:
            media_info = await MediaInfoUtility.get_media_info(file_link)
            print(f"Media info extraction successful, size: {len(media_info)} bytes")
        except Exception as e:
            print(f"Media info extraction failed: {e}")
            await progress_msg.edit_text(f"Media info extraction failed: {e}")
            return
        
        # Create a BytesIO object to send as a document
        media_info_file = io.BytesIO()
        media_info_file.name = f"mediainfo_{media_object.file_name if hasattr(media_object, 'file_name') else 'file'}.json"
        media_info_file.write(media_info)
        media_info_file.seek(0)
        
        # Send the media info file
        print("Sending media info document...")
        await reply.reply_document(
            document=media_info_file,
            caption="Media Information",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Made with ❤️", callback_data="about")]
            ])
        )
        
        # Update the progress message
        elapsed_time = time.time() - start_time
        print(f"Process completed in {elapsed_time:.2f} seconds")
        await progress_msg.edit_text(
            Messages.PROCESS_UPLOAD_CONFIRM.format(
                total_process_duration=str(datetime.timedelta(seconds=int(elapsed_time)))
            )
        )
        
    except FloodWait as e:
        print(f"FloodWait: {e}")
        await asyncio.sleep(e.x)
        await progress_msg.edit_text(f"Rate limited. Please try again after {e.x} seconds.")
    except Exception as e:
        print(f"Unhandled error: {e}")
        await progress_msg.edit_text(f"An error occurred: {str(e)}")

# # Handle media files sent directly to the bot
# @app.on_message(filters.private & (filters.document | filters.video | filters.audio))
# async def media_handler(client, message):
#     print(f"Media message received from user {message.from_user.id}")
#     await message.reply_text(
#         "To get media info, reply to this message with /mediainfo",
#         quote=True
#     )

# Main function to run the bot
# async def main():
#     print("Starting Media Info Bot...")
#     await app.start()
#     print("Bot is running!")
    
#     # Keep the bot running
#     await asyncio.Future()

# # Run the bot
# if __name__ == "__main__":
#     try:
#         print("Initializing...")
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(main())
#     except KeyboardInterrupt:
#         print("Bot stopped by user")
#     except Exception as e:
#         print(f"Fatal error: {e}")


# import os
# import tempfile
# import logging
# from pyrogram import Client, filters
# from pyrogram.types import Message
# from pymediainfo import MediaInfo

# log = logging.getLogger(__name__)

# @Client.on_message(filters.command("mediainfo") & filters.reply)
# async def mediainfo_handler(client: Client, message: Message):
#     reply = message.reply_to_message

#     if not (reply.document or reply.video or reply.audio):
#         await message.reply("Please reply to a video, audio, or document.")
#         return

#     await message.reply("🔍 Processing MediaInfo...")

#     try:
#         with tempfile.TemporaryDirectory() as temp_dir:
#             file_path = await reply.download(file_name=os.path.join(temp_dir, "media"))

#             media_info = MediaInfo.parse(file_path)
#             output_text = media_info.to_json()

#             if len(output_text) < 4096:
#                 await message.reply(f"📄 MediaInfo:\n```\n{output_text[:4000]}\n```", quote=True, parse_mode="markdown")
#             else:
#                 output_file_path = os.path.join(temp_dir, "mediainfo.json")
#                 with open(output_file_path, "w") as f:
#                     f.write(output_text)

#                 await message.reply_document(document=output_file_path, caption="📄 MediaInfo", quote=True)
#     except Exception as e:
#         log.exception("MediaInfo extraction failed.")
#         await message.reply("❌ Failed to extract MediaInfo.")
