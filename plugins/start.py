from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from helper.database import db
from config import Config, Txt
import humanize
from time import sleep


@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):

    if message.from_user.id in Config.BANNED_USERS:
        await message.reply_text("Sorry, You are banned.")
        return

    user = message.from_user
    await db.add_user(client, message)
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton('⚔️ Aʙᴏᴜᴛ', callback_data='about'),
        InlineKeyboardButton('⚙️ Hᴇʟᴩ', callback_data='help')
    ]])
    if Config.START_PIC:
        await message.reply_photo(Config.START_PIC, caption=Txt.START_TXT.format(user.mention), reply_markup=button)
    else:
        await message.reply_text(text=Txt.START_TXT.format(user.mention), reply_markup=button, disable_web_page_preview=True)


DOC = InlineKeyboardMarkup([
    [InlineKeyboardButton("Document ✅", callback_data="upload_document_on"), 
     InlineKeyboardButton("Video", callback_data="upload_video_on")],  
    [InlineKeyboardButton("Close", callback_data="close")]
])

VID = InlineKeyboardMarkup([
    [InlineKeyboardButton("Document", callback_data="upload_document_on"), 
     InlineKeyboardButton("Video ✅", callback_data="upload_video_on")],  
    [InlineKeyboardButton("Close", callback_data="close")]
])

CLS = InlineKeyboardMarkup(
    [[InlineKeyboardButton("Close", callback_data="close")]]
    )

@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    if data == "start":
        await query.message.edit_text(
            text=Txt.START_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton('⚔️ Aʙᴏᴜᴛ', callback_data='about'),
                InlineKeyboardButton('⚙️ Hᴇʟᴩ', callback_data='help')
            ]])
        )
    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✘ Cʟᴏꜱᴇ", callback_data="close"),
                InlineKeyboardButton("⟪ Bᴀᴄᴋ", callback_data="start")
            ]])
        )
    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT.format(client.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✘ Cʟᴏꜱᴇ", callback_data="close"),
                InlineKeyboardButton("⟪ Bᴀᴄᴋ", callback_data="start")
            ]])
        )


    elif data == "upload_document_on":
        await db.set_upload_type(user_id, "document")
        await query.message.edit_text(text="Your current upload format : **Document**.", disable_web_page_preview=True, reply_markup=DOC)
        print(f"Set upload type to Document for user_id={user_id}")
        
    elif data == "upload_video_on":
        await db.set_upload_type(user_id, "video")
        await query.message.edit_text(text="Your current upload format : **Video**.", disable_web_page_preview=True, reply_markup=VID)
        print(f"Set upload type to Video for user_id={user_id}")


    
    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
#            await query.message.continue_propagation()
        except:
            await query.message.delete()
#            await query.message.continue_propagation()



from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from helper.database import db


#    print(f"Current upload type for user_id={message.from_user.id} is {upload_type}")
#    await ms.delete()
    


    
# Handle callback queries
# @Client.on_callback_query()
# async def handle_callback_query(client, query: CallbackQuery):
#     data = query.data
#     user_id = query.from_user.id
#     print(f"Callback query received: data={data}, user_id={user_id}")

#     try:
#         if data == "upload_document_on":
#             await db.set_upload_type(user_id, "document")
#             await query.message.edit_text(text="Your current upload format : **Document**.", disable_web_page_preview=True, reply_markup=DOC)
#             print(f"Set upload type to Document for user_id={user_id}")
        
#         elif data == "upload_video_on":
#             await db.set_upload_type(user_id, "video")
#             await query.message.edit_text(text="Your current upload format : **Video**.", disable_web_page_preview=True, reply_markup=VID)
#             print(f"Set upload type to Video for user_id={user_id}")
        
#         elif data == "close":
#             await query.message.delete()
#             print(f"Closed message for user_id={user_id}")
#     except Exception as e:
#         print(f"Error handling callback query for user_id={user_id}: {e}")



@Client.on_message(filters.private & filters.command('upload'))
async def handle_id_command(client, message):

    if message.from_user.id not in Config.ADMIN:
        await message.reply_text("**Access Denied** ⚠️ \nError: You are not authorized to use my features")
        return
    
    ms = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)
    upload_type = await db.get_upload_type(message.from_user.id)
    await ms.delete()


    if upload_type == "document":
        await message.reply_text(f"Your current upload format : **Document**.", reply_markup=DOC)
        print(f"Reply sent: Current upload format is Document for user_id={message.from_user.id}")
    elif upload_type == "video":
        await message.reply_text(f"Your current upload format : **Video**.", reply_markup=VID)
        print(f"Reply sent: Current upload format is Video for user_id={message.from_user.id}")
        
@Client.on_message(filters.private & filters.command('imp_notes'))
async def imp(client, message):
    
    if message.from_user.id not in Config.ADMIN:
        await message.reply_text("**Access Denied** ⚠️ \nError: You are not authorized to use my features")
        return
        
    await message.reply_text("If Prefix/Suffix or both don't existed and you are\nadding yours Prefix/Suffix then use space in it\n\nspace = '-s'\nSet Prefix = {prefix}-s\nSet Suffix = -s{suffix}\n\nIf you are removing existed Prefix/Suffix by using Remname and\nAdding your Prefix/Suffix  then don't use space in it\n\nspace = '-s'\nSet Prefix = {prefix}\nSet Suffix = {suffix}", reply_markup=CLS)


