from pyrogram import Client, filters
from helper.database import db  # Assuming db is your Database class instance
from config import Config

# REMNAME
@Client.on_message(filters.private & filters.command('set_remname'))
async def add_remname(client, message):
    
    if message.from_user.id not in Config.ADMIN:
        await message.reply_text("**Access Denied** ⚠️ \nError: You are not authorized to use my features")
        return
        
    if len(message.command) == 1:
        return await message.reply_text("**__Give The Remname Text__\n\nExample:- `/set_remname Text1, Text2, Text3 [Max 5 Words]`**")
    
    # Get the entire text provided in the command
    remname_text = message.text.split(' ', 1)[1]

    SnowDev = await message.reply_text("Please Wait ...")
    await db.set_remname(message.from_user.id, remname_text)
    
    await SnowDev.edit("**Remname Text Saved Successfully ✅**")

@Client.on_message(filters.private & filters.command('del_remname'))
async def delete_remname(client, message):
    SnowDev = await message.reply_text("Please Wait ...")
    await db.delete_remname(message.from_user.id)
    await SnowDev.edit("**Remname Text Deleted Successfully 🗑️**")

@Client.on_message(filters.private & filters.command('see_remname'))
async def see_remname(client, message):
    SnowDev = await message.reply_text("Please Wait ...")
    remname_text = await db.get_remname(message.from_user.id)
    if remname_text:
        await SnowDev.edit(f"**Your Remname Texts:-**\n\n`{remname_text}`")
    else:
        await SnowDev.edit("**You Don't Have Any Remname Texts ❌**")

def remove_text_from_filename(filename, text_to_remove):
    """
    Removes the specified text from the given filename.
    Args:
        filename (str): The filename from which to remove the text.
        text_to_remove (str): The text to remove from the filename.
    Returns:
        str: The modified filename with the specified text removed.
    """
    return filename.replace(text_to_remove, "")
