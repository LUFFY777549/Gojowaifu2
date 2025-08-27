import time
from TEAMZYRO import app, sudo_users
from pyrogram import Client, filters
from pyrogram.types import Message

@app.on_message(filters.command("ping") & filters.user(sudo_users))
async def ping(client: Client, message: Message):
    user_id = str(message.from_user.id)
    
    if user_id not in sudo_users:
        await message.reply_text("Nouu.. its Sudo user's Command..")
        return

    start_time = time.time()
    sent = await message.reply_text("Pong!")
    end_time = time.time()
    elapsed_time = round((end_time - start_time) * 1000, 3)
    await sent.edit_text(f"Pong! {elapsed_time}ms")