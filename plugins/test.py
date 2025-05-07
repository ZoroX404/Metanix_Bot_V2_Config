import os
import tempfile
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pymediainfo import MediaInfo

log = logging.getLogger(__name__)

@Client.on_message(filters.command("mediainfo") & filters.reply)
async def mediainfo_handler(client: Client, message: Message):
    reply = message.reply_to_message

    if not (reply.document or reply.video or reply.audio):
        await message.reply("Please reply to a video, audio, or document.")
        return

    await message.reply("🔍 Processing MediaInfo...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = await reply.download(file_name=os.path.join(temp_dir, "media"))

            media_info = MediaInfo.parse(file_path)
            output_text = media_info.to_json()

            if len(output_text) < 4096:
                await message.reply(f"📄 MediaInfo:\n```\n{output_text[:4000]}\n```", quote=True, parse_mode="markdown")
            else:
                output_file_path = os.path.join(temp_dir, "mediainfo.json")
                with open(output_file_path, "w") as f:
                    f.write(output_text)

                await message.reply_document(document=output_file_path, caption="📄 MediaInfo", quote=True)
    except Exception as e:
        log.exception("MediaInfo extraction failed.")
        await message.reply("❌ Failed to extract MediaInfo.")
