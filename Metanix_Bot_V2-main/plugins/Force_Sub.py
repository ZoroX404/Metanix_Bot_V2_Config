from pyrogram import Client, filters, enums 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant
from config import Config
from helper.database import db

async def not_subscribed(_, client, message):
    await db.add_user(client, message)
    if not Config.FORCE_SUB:
        return False
    try:             
        user = await client.get_chat_member(Config.FORCE_SUB, message.from_user.id) 
        if user.status == enums.ChatMemberStatus.BANNED:
            return True 
        else:
            return False                
    except UserNotParticipant:
        pass
    return True


@Client.on_message(filters.private & filters.create(not_subscribed))
async def forces_sub(client, message):
    buttons = [[InlineKeyboardButton(text="𝙅𝙤𝙞𝙣 𝘾𝙝𝙖𝙣𝙣𝙚𝙡", url=f"https://t.me/{Config.FORCE_SUB}") ]]
    text = "**Sᴏʀʀy Dᴜᴅᴇ, Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ Jᴏɪɴ ᴏᴜʀ Cʜᴀɴɴᴇʟ ғɪʀsᴛ ᴏɴʟʏ ᴀғᴛᴇʀ ᴛʜᴀᴛ Yᴏᴜ ᴄᴀɴ ᴀʙʟᴇ ᴛᴏ ᴀᴄᴄᴇss ᴍᴇ.**"
    try:
        user = await client.get_chat_member(Config.FORCE_SUB, message.from_user.id)    
        if user.status == enums.ChatMemberStatus.BANNED:                                   
            return await client.send_message(message.from_user.id, text="Sᴏʀʀy Yᴏᴜ'ʀᴇ Bᴀɴɴᴇᴅ Tᴏ Uꜱᴇ Mᴇ")  
    except UserNotParticipant:                       
        return await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
          



