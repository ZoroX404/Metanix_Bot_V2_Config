import os
import tempfile
from pyrogram import Client, filters
from pyrogram.types import Message
from pymediainfo import MediaInfo


@Client.on_message(filters.command("mediainfo") & filters.reply)
async def partial_mediainfo(client: Client, message: Message):
    reply = message.reply_to_message

    if not (reply and (reply.document or reply.video or reply.audio)):
        return await message.reply("❌ Reply to a valid media file (video, audio, or document).")

    msg = await message.reply("📥 Fetching partial media...")

    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            async for chunk in reply.stream():
                temp_file.write(chunk)
                if temp_file.tell() > 5 * 1024 * 1024:  # Limit to 5 MB
                    break
            temp_file.flush()
            temp_path = temp_file.name

        media_info = MediaInfo.parse(temp_path)
        info_text = ""

        for track in media_info.tracks:
            for key, value in track.to_data().items():
                info_text += f"{key}: {value}\n"
            info_text += "\n---\n"

        if not info_text.strip():
            info_text = "⚠️ No metadata found."

        # Truncate to Telegram's message length limit
        await msg.edit_text(info_text[:4096])

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n`{e}`")

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
