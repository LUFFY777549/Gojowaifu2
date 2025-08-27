from TEAMZYRO import app, group_user_totals_collection, send_image
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message

# Global locks & cooldowns
locks = {}                # chat_id -> asyncio.Lock()
user_cooldowns = {}       # user_id -> cooldown end timestamp
warned_users = {}         # user_id -> last warning timestamp
last_user = {}            # chat_id -> {'user_id': user_id, 'count': N}
normal_message_counts = {}  # chat_id -> message count

DEFAULT_CTIME = 80  # Default messages per drop

@app.on_message(filters.private | filters.group)
async def message_counter(client: Client, message: Message):
    chat_id = str(message.chat.id)
    user_id = message.from_user.id
    current_time = time.time()

    # Fetch or initialize group data
    existing_group = await group_user_totals_collection.find_one({"group_id": chat_id})
    if not existing_group:
        await group_user_totals_collection.update_one(
            {"group_id": chat_id}, 
            {"$set": {"group_id": chat_id, "ctime": DEFAULT_CTIME}}, 
            upsert=True
        )
        ctime = DEFAULT_CTIME
    else:
        ctime = existing_group.get("ctime", DEFAULT_CTIME)

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
        # User cooldown check
        if user_id in user_cooldowns:
            cooldown_end = user_cooldowns[user_id]
            if current_time < cooldown_end:
                return
            else:
                del user_cooldowns[user_id]

        # Spam detection
        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:
                if user_id not in warned_users or current_time - warned_users[user_id] >= 600:
                    cooldown_end = current_time + 600  # 10 min block
                    user_cooldowns[user_id] = cooldown_end
                    warned_users[user_id] = current_time
                    await message.reply(
                        f"⚠️ Don't Spam {message.from_user.first_name}...\n"
                        "Your messages will be ignored for 10 minutes..."
                    )
                return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        # Normal message counting for drops
        if chat_id in normal_message_counts:
            normal_message_counts[chat_id] += 1
        else:
            normal_message_counts[chat_id] = 1

        if normal_message_counts[chat_id] % ctime == 0:
            await send_image(message)  # Send character drop
            normal_message_counts[chat_id] = 0  # Reset count