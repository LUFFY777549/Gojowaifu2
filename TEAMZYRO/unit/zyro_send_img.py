from TEAMZYRO import *
import random
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message

log = "-1002527530412"

async def delete_message(chat_id, message_id):
    await asyncio.sleep(300)  # 5 minutes
    try:
        await app.delete_messages(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

RARITY_WEIGHTS = {
    "⚪️ Low": (40, True),
    "🟠 Medium": (20, True),
    "🔴 High": (12, True),
    "🎩 Special Edition": (8, True),
    "🪽 Elite Edition": (6, True),
    "🪐 Exclusive": (4, True),
    "💞 Valentine": (2, False),
    "🎃 Halloween": (2, False),
    "❄️ Winter": (1.5, False),
    "🏖 Summer": (1.2, False),
    "🎗 Royal": (0.5, False),
    "💸 Luxury Edition": (0.5, False)
}

@Client.on_message(filters.command("send_image"))
async def send_image(client: Client, message: Message):
    chat_id = message.chat.id

    all_characters = list(await collection.find({
        "rarity": {"$in": [k for k, v in RARITY_WEIGHTS.items() if v[1]]}
    }).to_list(length=None))

    if not all_characters:
        await message.reply_text("No characters found with allowed rarities in the database.")
        return

    available_characters = [
        c for c in all_characters
        if 'id' in c and c.get('rarity') and RARITY_WEIGHTS.get(c['rarity'], (0, False))[1]
    ]

    if not available_characters:
        await message.reply_text("No available characters with the allowed rarities.")
        return

    # Weighted random selection
    cumulative_weights = []
    cumulative_weight = 0
    for character in available_characters:
        cumulative_weight += RARITY_WEIGHTS.get(character.get('rarity'), (1, False))[0]
        cumulative_weights.append(cumulative_weight)

    rand = random.uniform(0, cumulative_weight)
    selected_character = None
    for i, character in enumerate(available_characters):
        if rand <= cumulative_weights[i]:
            selected_character = character
            break

    if not selected_character:
        selected_character = random.choice(available_characters)

    last_characters[chat_id] = selected_character
    last_characters[chat_id]['timestamp'] = time.time()

    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    # Send photo or video
    if 'vid_url' in selected_character:
        sent_msg = await message.reply_video(
            video=selected_character['vid_url'],
            caption=f"✨ A {selected_character['rarity']} Character Appears! ✨\n🔍 Use /guess to claim this mysterious character!\n💫 Hurry, before someone else snatches them!"
        )
    else:
        sent_msg = await message.reply_photo(
            photo=selected_character['img_url'],
            caption=f"✨ A {selected_character['rarity']} Character Appears! ✨\n🔍 Use /guess to claim this mysterious character!\n💫 Hurry, before someone else snatches them!"
        )

    # Schedule message deletion after 5 minutes
    asyncio.create_task(delete_message(chat_id, sent_msg.message_id))