import subprocess
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config 

log = logging.getLogger(__name__)

BOT_TOKEN = Config.BOT_TOKEN

@Client.on_message(filters.command("mediainfo") & filters.reply)
async def mediainfo_remote_handler(client: Client, message: Message):
    reply = message.reply_to_message

    # Check if media is present (video, audio, or document)
    media = reply.document or reply.video or reply.audio
    if not media:
        await message.reply("❌ Please reply to a media file.")
        return

    try:
        status = await message.reply("🔍 Getting Telegram CDN URL...")

        # Step 1: Get file info from Telegram
        # Handle different types of media
        file_id = None
        if reply.document:
            file_id = reply.document.file_id
        elif reply.video:
            file_id = reply.video.file_id
        elif reply.audio:
            file_id = reply.audio.file_id

        # Ensure we have a file_id
        if not file_id:
            await message.reply("❌ Unable to retrieve file_id.")
            return

        # Get the file info from Telegram
        telegram_file = client.get_file(file_id)
        file_path = telegram_file.file_path
        cdn_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

        # Step 2: Use ffprobe to fetch media info from the URL
        command = [
            "ffprobe",
            "-v", "error",
            "-show_format",
            "-show_streams",
            "-of", "json",
            cdn_url
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"ffprobe error: {result.stderr}")

        output = result.stdout

        # Step 3: Send result
        if len(output) < 4096:
            await status.edit(f"📄 MediaInfo:\n```\n{output[:4000]}\n```", parse_mode="markdown")
        else:
            await status.edit("📄 MediaInfo is too large to display. You can use `/download` to get the full file.")
    except Exception as e:
        log.exception("Error in remote mediainfo handler")
        await message.reply("❌ Failed to get MediaInfo from Telegram CDN.")
