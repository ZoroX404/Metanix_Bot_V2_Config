import time
import os
import asyncio
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from plugins.remname import remove_text_from_filename  # Import the necessary function from remname.py

async def fix_thumb(thumb):
    width = 0
    height = 0
    try:
        if thumb is not None:
            parser = createParser(thumb)
            metadata = extractMetadata(parser)
            if metadata.has("width"):
                width = metadata.get("width")
            if metadata.has("height"):
                height = metadata.get("height")

            with Image.open(thumb) as img:
                img.convert("RGB").save(thumb)
                resized_img = img.resize((width, height))
                resized_img.save(thumb, "JPEG")
            parser.close()
    except Exception as e:
        print(e)
        thumb = None

    return width, height, thumb

async def take_screen_shot(video_file, output_directory, ttl, remname_text):
    out_put_file_name = f"{output_directory}/{time.time()}.jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        # Remove specified text from the output file name
        out_put_file_name = remove_text_from_filename(out_put_file_name, remname_text)
        return out_put_file_name
    return None
