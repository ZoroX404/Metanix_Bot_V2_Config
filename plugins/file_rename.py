import random
import asyncio
import os
import time
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image

from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix, add_sprefix_suffix, add_prefix_ssuffix, add_sprefix_ssuffix
from helper.ffmpeg import fix_thumb, take_screen_shot
from helper.database import db
from config import Config, UPLOAD_CANCEL
from pyrogram.types import CallbackQuery

app = Client("test", api_id=Config.STRING_API_ID, api_hash=Config.STRING_API_HASH, session_string=Config.STRING_SESSION)

@Client.on_callback_query(filters.regex("cancel"))
async def cancel_callback(bot, query: CallbackQuery):
    print("cancel called.................")

    try:
        user_id = query.from_user.id
        msg_id = query.message.id
        msg_key = f"{user_id}_{msg_id}"
        UPLOAD_CANCEL[msg_key] = True
        await query.answer("Cancelled ❌", show_alert=False)
        await query.message.delete()
        cancel_msg = await bot.send_message(
            chat_id=query.message.chat.id,
            text="Cancelled ❌"
        )
        await asyncio.sleep(10)
        await cancel_msg.delete()
    except Exception as e:
        print(f"Cancel error: {e}")

# Define the callback for the 'upload' buttons
@Client.on_message(filters.private & (filters.document | filters.audio | filters.video) & filters.user(Config.ADMIN))
async def rename(bot, message):
    
    auto_type = await db.get_auto(message.from_user.id)
    if auto_type == False:
        warning = await message.reply_text("⚠️ Your Auto Rename Status is OFF use /auto if you want to Turn it ON")
        await asyncio.sleep(10)
        
        # Delete the warning message
        try:
            await warning.delete()
        except Exception as e:
            print(f"Failed to delete warning message: {e}")
        return
        
    print("Function called")
    file = getattr(message, message.media.value)

    filename = file.file_name  
    if file.file_size > 2000 * 1024 * 1024:
         return await message.reply_text("⚠️ Sorry Bro This Bot Doesn't Support Uploading Files Bigger Than 2GB")


#    if message.document:
#        file_id = message.document.file_id
#        file_name = message.document.file_name
#        media_type = media_preference or "document"  # Use preferred media type or default to document
 #       print("Document detected")
#    elif message.video:
 #       file_id = message.video.file_id
 #       file_name = f"{message.video.file_name}.mp4"
#       media_type = media_preference or "video"  # Use preferred media type or default to video
 #       print("Video detected")
 #   else:
 #       print("Unsupported file type")
 #       return await message.reply_text("Unsupported File Type")
#

    if not os.path.isdir("Metadata"):
        os.mkdir("Metadata")
        
    prefix = await db.get_prefix(message.chat.id)
    suffix = await db.get_suffix(message.chat.id)
    space = "-s"
    print(f"Prefix: {prefix}, Suffix: {suffix}")

    
    new_filename_  = file.file_name 
    print(f"Filename: {new_filename_}")
 #   new_filename_ = new_name.split(":-")[1]
    remname_text = await db.get_remname(message.chat.id)  # Get the remname text from the user's database entry

    if remname_text:
        print("Remname presents")
        split_text = remname_text.split(', ')

        remname1 = split_text[0] if len(split_text) > 0 else None
        remname2 = split_text[1] if len(split_text) > 1 else None
        remname3 = split_text[2] if len(split_text) > 2 else None
        remname4 = split_text[3] if len(split_text) > 3 else None
        remname5 = split_text[4] if len(split_text) > 4 else None
        remname6 = split_text[5] if len(split_text) > 5 else None
        remname7 = split_text[6] if len(split_text) > 6 else None
        remname8 = split_text[7] if len(split_text) > 7 else None
        remname9 = split_text[8] if len(split_text) > 8 else None
        remname10 = split_text[9] if len(split_text) > 9 else None
        
        if remname1 and remname1 in new_filename_:
            new_filename_ = new_filename_.replace(remname1, "")  # Remove the remname text from the new filename
            print(f"Remname text: {remname_text} removed from filename")
        
        if remname2 and remname2 in new_filename_:
            new_filename_ = new_filename_.replace(remname2, "")  # Remove the remname text from the new filename
        
        if remname3 and remname3 in new_filename_:
            new_filename_ = new_filename_.replace(remname3, "")  # Remove the remname text from the new filename
        
        if remname4 and remname4 in new_filename_:
            new_filename_ = new_filename_.replace(remname4, "")  # Remove the remname text from the new filename
        
        if remname5 and remname5 in new_filename_:
            new_filename_ = new_filename_.replace(remname5, "")  # Remove the remname text from the new filename

        if remname6 and remname6 in new_filename_:
            new_filename_ = new_filename_.replace(remname6, "")  # Remove the remname text from the new filename
            print(f"Remname text: {remname_text} removed from filename")
        
        if remname7 and remname7 in new_filename_:
            new_filename_ = new_filename_.replace(remname7, "")  # Remove the remname text from the new filename
        
        if remname8 and remname8 in new_filename_:
            new_filename_ = new_filename_.replace(remname8, "")  # Remove the remname text from the new filename
        
        if remname9 and remname9 in new_filename_:
            new_filename_ = new_filename_.replace(remname9, "")  # Remove the remname text from the new filename
        
        if remname10 and remname10 in new_filename_:
            new_filename_ = new_filename_.replace(remname10, "")  # Remove the remname text from the new filename
        

    try:

        prefix = await db.get_prefix(message.chat.id)
        suffix = await db.get_suffix(message.chat.id)
        space = "-s"
        
        if prefix is None and suffix is None:
                
                new_filename = add_prefix_suffix(new_filename_, prefix, suffix)

        elif prefix is None:
            if space in suffix:
                suffix = suffix.replace(space, "")
                new_filename = add_prefix_ssuffix(new_filename_, prefix, suffix)
            else:
                new_filename = add_prefix_suffix(new_filename_, prefix, suffix)

        elif suffix is None:
            if space in prefix:
                prefix = prefix.replace(space, "")
                new_filename = add_sprefix_suffix(new_filename_, prefix, suffix)
            else:
                new_filename = add_prefix_suffix(new_filename_, prefix, suffix)

        else:
            if space in prefix and space not in suffix:
                prefix = prefix.replace(space, "")
                new_filename = add_sprefix_suffix(new_filename_, prefix, suffix)

            elif space not in prefix and space in suffix:
                suffix = suffix.replace(space, "")
                new_filename = add_prefix_ssuffix(new_filename_, prefix, suffix)

            elif space in prefix and space in suffix:
                prefix = prefix.replace(space, "")
                suffix = suffix.replace(space, "")
                new_filename = add_sprefix_ssuffix(new_filename_, prefix, suffix)

            else:
                new_filename = add_prefix_suffix(new_filename_, prefix, suffix)

            
        print(f"New filename: {new_filename}")
    except Exception as e:
        print(f"Error setting prefix/suffix: {e}")
        return await message.edit(f"⚠️ Something went wrong, can't set Prefix or Suffix \nError: {e}")

    file_path = f"downloads/{new_filename}"
    file = message

    ms = await message.reply_text(text="Trying To Download.....",  reply_to_message_id=file.id)
    msg_key = f"{message.chat.id}_{ms.id}"
    UPLOAD_CANCEL[msg_key] = False
    try:
        path = await bot.download_media(message=file, file_name=file_path,  progress=progress_for_pyrogram, progress_args=("**Download Started.... **", ms, time.time()))
        print(f"File downloaded to {path}")
        if UPLOAD_CANCEL.get(msg_key):
            if os.path.exists(file_path):
                os.remove(file_path)
            raise Exception("Cancelled by user")
            print("cancled")
    except Exception as e:
        print(f"Error downloading media: {e}")
        return await ms.edit(e)

    _bool_metadata = await db.get_metadata(message.chat.id)

    if (_bool_metadata):
        metadata_path = f"Metadata/{new_filename}"
        metadata = await db.get_metadata_code(message.chat.id)
        if metadata:

            await ms.edit("I Fᴏᴜɴᴅ Yᴏᴜʀ Mᴇᴛᴀᴅᴀᴛᴀ\n\n**Aᴅᴅɪɴɢ Mᴇᴛᴀᴅᴀᴛᴀ Tᴏ Fɪʟᴇ....**")
            cmd = f"""ffmpeg -nostdin -y -i "{path}" {metadata} "{metadata_path}" """

            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            er = stderr.decode()

            try:
                if er:
                    print(er) 
                    return await ms.edit(str(er) + "\n\n**Error**")
            except BaseException:
                pass
        await ms.edit("**Mᴇᴛᴀᴅᴀᴛᴀ ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ ғɪʟᴇ sᴜᴄᴄᴇssғᴜʟʟʏ ✅**\n\n**Tʀyɪɴɢ Tᴏ Uᴩʟᴏᴀᴅɪɴɢ....**")
                
    else:
        print("No metadata to add")
        await ms.edit("**Trying to Upload....**")

    duration = 0
    try:
        parser = createParser(file_path)
        metadata = extractMetadata(parser)
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        parser.close()
        print(f"File duration: {duration}")
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        pass

    ph_path = None
    media = getattr(file, file.media.value)
    c_caption = await db.get_caption(message.chat.id)
    c_thumb = await db.get_thumbnail(message.chat.id)

    if c_caption:
        try:
            caption = c_caption.format(filename=new_filename, filesize=humanbytes(media.file_size), duration=convert(duration))
            print(f"Caption: {caption}")
        except Exception as e:
            print(f"Caption error: {e}")
            return await ms.edit(text=f"Your Caption Error Exception ●> ({e})")
    else:
        caption = f"**{new_filename}**"
        print(f"Default caption: {caption}")

    if c_thumb:
        # Use custom thumbnail if provided
        ph_path = await bot.download_media(c_thumb)
        width, height, ph_path = await fix_thumb(ph_path)
        print(f"Custom thumbnail path: {ph_path}")
    elif media.thumbs:
        # Use the media's own thumbnail if available
        ph_path = await bot.download_media(media.thumbs[0].file_id)
        width, height, ph_path = await fix_thumb(ph_path)
        print(f"Media thumbnail path: {ph_path}")
    else:
        # Only generate screenshot if no thumbnails are available
        try:
            ph_path_ = await take_screen_shot(file_path, os.path.dirname(os.path.abspath(file_path)), random.randint(0, duration - 1))
            width, height, ph_path = await fix_thumb(ph_path_)
            print(f"Generated thumbnail path: {ph_path}")
        except Exception as e:
            ph_path = None
            print(f"Error generating thumbnail: {e}")

    upload_type = await db.get_upload_type(message.from_user.id)
    print(f"Upload type: {upload_type}")

    if media.file_size > 2000 * 1024 * 1024:
        try:
            if upload_type == "document":
                filw = await app.send_document(
                    Config.LOG_CHANNEL,
                    document=metadata_path if _bool_metadata else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("**Upload Started....**", ms, time.time())
                )
                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(message.from_user.id, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)
                print("Document uploaded")
            elif upload_type == "video":
                filw = await app.send_video(
                    message.chat.id,
                    video=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    width=width,
                    height=height,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("**Upload Started....**", ms, time.time())
                )
                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(message.from_user.id, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)
                print("Video uploaded")
        except Exception as e:
            print(f"Upload error: {e}")
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            if metadata_path:
                os.remove(metadata_path)
            if path:
                os.remove(path)
            return await ms.edit(f" Error {e}")
    else:
        try:
            if upload_type == "document":
                await bot.send_document(
                    message.chat.id,
                    document=metadata_path if _bool_metadata else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("**Upload Started....**", ms, time.time())
                )
                print("Document uploaded")
            elif upload_type == "video":
                await bot.send_video(
                    message.chat.id,
                    video=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    width=width,
                    height=height,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("**Upload Started....**", ms, time.time())
                )
                print("Video uploaded")
        except Exception as e:
            print(f"Upload error: {e}")
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            if metadata_path:
                os.remove(metadata_path)
            if path:
                os.remove(path)
            return await ms.edit(f" Error {e}")

    await ms.delete()
    print("Message deleted")

    if ph_path:
        os.remove(ph_path)
    if file_path:
        os.remove(file_path)
    if metadata_path:
        os.remove(metadata_path)
    print("Temporary files removed")
