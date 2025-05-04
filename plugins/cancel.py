from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from config import UPLOAD_CANCEL

@Client.on_callback_query(filters.regex(r"^cancel:(.+)"))
async def cancel_upload(client: Client, query: CallbackQuery):
    # Extract the msg_id key
    msg_id = query.data.split(":", 1)[1]
    # Set flag
    UPLOAD_CANCEL[msg_id] = True

    # Acknowledge to user
    await query.answer("Process cancelled ❌", show_alert=False)
    # Optionally update the button text
    try:
        await query.message.edit("❌ Process cancelled by user.")
    except:
        pass
