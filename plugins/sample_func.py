from pyrogram import Client, filters
from pyrogram.types import Message
import os
import time
import random
import asyncio
import aiohttp
from pyrogram import Client, filters
from config import Config


app = Client("test", api_id=Config.STRING_API_ID, api_hash=Config.STRING_API_HASH, session_string=Config.STRING_SESSION)

@app.on_message(filters.private & filters.command("sv"))
async def sample_video_handler(client, message: Message):
    print(f"Command received: {message.command}")

    replied = message.reply_to_message
    if not replied:
        return await message.reply("❌ Please reply to a video message when using this command.")

    if len(message.command) == 1:
        return await message.reply_text("❗ Usage: Reply to a video with `/sv <duration-in-seconds>`", parse_mode="markdown")

    if len(message.command) > 2:
        return await message.reply_text("❗ Usage: Reply to a video with `/sv <duration-in-seconds>` (only one number)", parse_mode="markdown")

    if not (replied.video or replied.document):
        return await message.reply("❌ This command only works on actual videos or video documents.")

    try:
        sample_duration = int(message.command[1])
        if sample_duration <= 0:
            return await message.reply("❌ Duration must be a positive number.")
    except ValueError:
        return await message.reply("❌ Duration must be a number.")

    status_msg = await message.reply_text("⏳ Analyzing video...")

    try:
        file_id = replied.video.file_id if replied.video else replied.document.file_id
        file_info = await client.get_file(file_id)
        file_path = file_info.file_path

        # Attempt to get video duration
        probe_cmd = (
            f'ffprobe -v error -select_streams v:0 -show_entries format=duration '
            f'-of default=noprint_wrappers=1:nokey=1 "tg://{file_path}"'
        )
        process = await asyncio.create_subprocess_shell(
            probe_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()

        try:
            actual_duration = float(stdout.decode().strip())
            if sample_duration > actual_duration:
                return await status_msg.edit(
                    f"❌ Given duration ({sample_duration}s) is longer than the actual video duration ({actual_duration:.1f}s)."
                )
        except (ValueError, IndexError):
            await status_msg.edit("⚠️ Couldn't determine video duration. Processing anyway...")
            actual_duration = 3600

        max_start = max(0, int(actual_duration - sample_duration))
        start_time = random.randint(0, max_start)

        await status_msg.edit(f"✂️ Extracting {sample_duration}s segment from position {start_time}s...")

        os.makedirs("downloads", exist_ok=True)
        output_path = f"downloads/sample_{message.from_user.id}_{int(time.time())}_{sample_duration}s.mp4"

        ffmpeg_cmd = (
            f'ffmpeg -ss {start_time} -i "tg://{file_path}" -t {sample_duration} '
            f'-c:v copy -c:a copy -avoid_negative_ts 1 -movflags +faststart "{output_path}" -y'
        )
        process = await asyncio.create_subprocess_shell(
            ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await process.communicate()

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            print("Direct method failed. Stderr:", stderr.decode())
            await status_msg.edit("⚠️ Direct processing failed. Using alternative method...")

            file_url = f"https://api.telegram.org/file/bot{client.bot_token}/{file_path}"
            bytes_per_second = 1_000_000
            start_byte = max(0, int((start_time - 5) * bytes_per_second))
            end_byte = int((start_time + sample_duration + 5) * bytes_per_second)
            temp_path = f"downloads/temp_{message.from_user.id}_{int(time.time())}.mp4"

            await status_msg.edit(f"📥 Downloading segment...")

            async with aiohttp.ClientSession() as session:
                headers = {"Range": f"bytes={start_byte}-{end_byte}"}
                async with session.get(file_url, headers=headers) as response:
                    if response.status == 206:
                        with open(temp_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                    else:
                        raise Exception(f"Failed to get byte range: HTTP {response.status}")

            fallback_cmd = (
                f'ffmpeg -ss 5 -i "{temp_path}" -t {sample_duration} '
                f'-c:v copy -c:a copy -movflags +faststart "{output_path}" -y'
            )
            process = await asyncio.create_subprocess_shell(fallback_cmd)
            await process.communicate()

            if os.path.exists(temp_path):
                os.remove(temp_path)

        await status_msg.edit("📤 Uploading sample video...")
        await message.reply_video(
            output_path,
            caption=f"🎬 Random {sample_duration}s sample (starts at {start_time}s)"
        )

        if os.path.exists(output_path):
            os.remove(output_path)

    except Exception as e:
        print(f"Error: {e}")
        await status_msg.edit("❌ An error occurred while processing your request.")
