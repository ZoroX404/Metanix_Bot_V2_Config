from config import Config
from helper.database import db
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
import os, sys, time, asyncio, logging, datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
 
@Client.on_message(filters.command(["stats", "status"]) & filters.user(Config.ADMIN))
async def get_stats(bot, message):


     
    total_users = await db.total_users_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - Config.BOT_UPTIME))    
    start_t = time.time()
    st = await message.reply('**Aᴄᴄᴇꜱꜱɪɴɢ Tʜᴇ Dᴇᴛᴀɪʟꜱ.....**')    
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await st.edit(text=f"**--Bᴏᴛ Sᴛᴀᴛᴜꜱ--** \n\n**⌚️ Bᴏᴛ Uᴩᴛɪᴍᴇ:** {uptime} \n**🐌 Cᴜʀʀᴇɴᴛ Pɪɴɢ:** `{time_taken_s:.3f} ᴍꜱ` \n**👭 Tᴏᴛᴀʟ Uꜱᴇʀꜱ:** `{total_users}`")


#Restart to cancell all process 
@Client.on_message(filters.private & filters.command("restart") & filters.user(Config.OWNER))
async def restart_bot(b, m):
    if m.from_user.id == Config.OWNER:
        logging.info("Restart command received from an authorized user")
        await m.reply_text("🔄__Restarting.....__")
        logging.info("Bot restarting...")
        os.execl(sys.executable, sys.executable, *sys.argv)
    else:
        logging.warning("Unauthorized user tried to restart the bot")
        await m.reply_text("**Access Denied** ⚠️ \nError: You are not authorized to use this feature")


@Client.on_message(filters.command("broadcast") & filters.user(Config.OWNER) & filters.reply)
async def broadcast_handler(bot: Client, m: Message):
    if m.from_user.id == Config.OWNER:
        await bot.send_message(Config.LOG_CHANNEL, f"{m.from_user.mention} or {m.from_user.id} is started the broadcast...")
        
        all_users = await db.get_all_users()
        broadcast_msg = m.reply_to_message
        sts_msg = await m.reply_text("Broadcast started!")
        done = 0
        failed = 0
        success = 0
        start_time = time.time()
        total_users = await db.total_users_count()

        async for user in all_users:
            sts = await send_msg(user['_id'], broadcast_msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await db.delete_user(user['_id'])
            done += 1
            if not done % 20:
                await sts_msg.edit(f"Broadcast in progress: \nTotal Users: {total_users} \nCompleted: {done}/{total_users}\nSuccess: {success}\nFailed: {failed}")

        completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
        await sts_msg.edit(f"Broadcast completed: \nCompleted in `{completed_in}`.\n\nTotal Users: {total_users}\nCompleted: {done}/{total_users}\nSuccess: {success}\nFailed: {failed}")
    else:
        await m.reply_text("**Access Denied** ⚠️ \nError: You are not authorized to use this feature")
async def send_msg(user_id, message):
    try:
        await message.forward(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        logger.info(f"{user_id} : Dᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ")
        return 400
    except UserIsBlocked:
        logger.info(f"{user_id} : Bʟᴏᴄᴋᴇᴅ Tʜᴇ Bᴏᴛ")
        return 400
    except PeerIdInvalid:
        logger.info(f"{user_id} : Uꜱᴇʀ Iᴅ Iɴᴠᴀʟɪᴅ")
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        return 500
 
