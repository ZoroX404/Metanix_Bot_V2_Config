from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging
from plugins.utils import Utilities
from config import Config
from plugins.messages import Messages as ms

logger = logging.getLogger(__name__)

# Reply to file messages with media info option
@Client.on_message(filters.private & filters.reply & ~filters.text)
async def media_info_reply_handler(client, message):
    """
    When user replies to a media message with '/mediainfo', 
    this handler processes the request
    """
    # Check if the message is replying to a valid media file
    replied_message = message.reply_to_message
    
    if not replied_message or not hasattr(replied_message, 'media'):
        await message.reply_text("Please reply to a valid media file.")
        return
    
    # Check if the user is requesting media info
    if message.text and message.text.lower() in ['/mediainfo', '/info', 'mediainfo']:
        await process_media_info_request(client, message, replied_message)

async def process_media_info_request(client, message, media_message):
    """
    Process a media info request for the replied file
    """
    progress_message = await message.reply_text(ms.PROCESSING_REQUEST)
    
    try:
        # Get file link - for Telegram files this might be a bot API file link
        # or for external URLs this might be the URL itself
        if hasattr(media_message, 'document'):
            file_obj = media_message.document
        elif hasattr(media_message, 'video'):
            file_obj = media_message.video
        elif hasattr(media_message, 'audio'):
            file_obj = media_message.audio
        else:
            await progress_message.edit_text("Unsupported media type.")
            return
            
        # Get a download link for the file - this is where the efficiency comes in!
        # Instead of downloading the entire file, we get a link that ffprobe/mediainfo can use
        if hasattr(file_obj, 'file_id'):
            # For Telegram files, we need to get a URL
            file_link = await client.get_file_link(file_obj.file_id)
        else:
            # For direct links shared in Telegram
            file_link = media_message.text
            
        logger.info(f"Processing media info for {file_link}")
        await progress_message.edit_text(ms.MEDIAINFO_START)
        
        # This is the efficient part - extract media info without full download
        media_info = await Utilities.get_media_info(file_link)
        
        # Send the media info back to the user
        media_info_file = io.BytesIO()
        media_info_file.name = "mediainfo.json"
        media_info_file.write(media_info)
        
        # Send the media info as a document
        await media_message.reply_document(
            document=media_info_file,
            quote=True,
            caption="Media Information",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Get Web URL", callback_data="webmi")]]
            ),
        )
        
        await progress_message.edit_text("Media info extracted successfully!")
        
    except Exception as e:
        logger.error(f"Error processing media info: {e}")
        await progress_message.edit_text(f"Failed to extract media info: {str(e)}")
        
        # Log the error
        if Config.LOG_CHANNEL:
            await client.send_message(
                Config.LOG_CHANNEL,
                f"Media info extraction failed for user {message.from_user.id}. Error: {str(e)}"
            )











# import os
# import tempfile
# from pyrogram import Client, filters
# from pyrogram.types import Message
# from pymediainfo import MediaInfo


# @Client.on_message(filters.command("mediainfo") & filters.reply)
# async def partial_mediainfo(client: Client, message: Message):
#     reply = message.reply_to_message

#     if not (reply and (reply.document or reply.video or reply.audio)):
#         return await message.reply("❌ Reply to a valid media file (video, audio, or document).")

#     msg = await message.reply("📥 Fetching partial media...")

#     try:
#         with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#             async for chunk in reply.stream():
#                 temp_file.write(chunk)
#                 if temp_file.tell() > 5 * 1024 * 1024:  # Limit to 5 MB
#                     break
#             temp_file.flush()
#             temp_path = temp_file.name

#         media_info = MediaInfo.parse(temp_path)
#         info_text = ""

#         for track in media_info.tracks:
#             for key, value in track.to_data().items():
#                 info_text += f"{key}: {value}\n"
#             info_text += "\n---\n"

#         if not info_text.strip():
#             info_text = "⚠️ No metadata found."

#         # Truncate to Telegram's message length limit
#         await msg.edit_text(info_text[:4096])

#     except Exception as e:
#         await msg.edit_text(f"❌ Error:\n`{e}`")

#     finally:
#         if os.path.exists(temp_path):
#             os.unlink(temp_path)
