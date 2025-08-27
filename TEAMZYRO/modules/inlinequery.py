import re
import time
from cachetools import TTLCache
from html import escape
from pyrogram import Client, filters
from pyrogram.types import InlineQuery, InlineQueryResultPhoto, InlineQueryResultVideo
from TEAMZYRO import app, user_collection, collection

# Caches
all_characters_cache = TTLCache(maxsize=10000, ttl=300)  # 5 minutes
user_collection_cache = TTLCache(maxsize=10000, ttl=30)  # 30 seconds

async def get_user_collection(user_id: int):
    user_id = str(user_id)
    if user_id in user_collection_cache:
        return user_collection_cache[user_id]

    user = await user_collection.find_one({'id': int(user_id)})
    if user:
        user_collection_cache[user_id] = user
    return user

async def search_characters(query: str, force_refresh=False):
    cache_key = f"search_{query.lower()}"
    if not force_refresh and cache_key in all_characters_cache:
        return all_characters_cache[cache_key]

    regex = re.compile(query, re.IGNORECASE)
    characters = await collection.find({
        "$or": [
            {"name": regex},
            {"anime": regex},
            {"aliases": regex}
        ]
    }).to_list(length=None)

    all_characters_cache[cache_key] = characters
    return characters

async def get_all_characters(force_refresh=False):
    if not force_refresh and 'all_characters' in all_characters_cache:
        return all_characters_cache['all_characters']

    characters = await collection.find({}).to_list(length=None)
    all_characters_cache['all_characters'] = characters
    return characters

async def refresh_character_caches():
    all_characters_cache.clear()
    user_collection_cache.clear()

# Pyrogram Inline Query handler
@app.on_inline_query()
async def inlinequery_handler(client: Client, query: InlineQuery):
    try:
        text = query.query.strip()
        offset = int(query.offset) if query.offset else 0
        force_refresh = "!refresh" in text
        if force_refresh:
            text = text.replace("!refresh", "").strip()
            await refresh_character_caches()

        # User collection query
        user = None
        if text.startswith("collection."):
            parts = text.split(" ")
            user_id = parts[0].split(".")[1]
            search_terms = " ".join(parts[1:]) if len(parts) > 1 else ""

            if user_id.isdigit():
                user = await get_user_collection(user_id)
                if user:
                    all_characters = list({char['id']: char for char in user.get('characters', []) if 'id' in char}.values())
                    if search_terms:
                        regex = re.compile(search_terms, re.IGNORECASE)
                        all_characters = [
                            char for char in all_characters
                            if regex.search(char.get('name', '')) or
                               regex.search(char.get('anime', '')) or
                               regex.search(" ".join(char.get('aliases', [])))
                        ]
                else:
                    all_characters = []
            else:
                all_characters = []
        else:
            if text:
                all_characters = await search_characters(text, force_refresh)
            else:
                all_characters = await get_all_characters(force_refresh)

        # Filter media type
        if ".AMV" in text:
            all_characters = [c for c in all_characters if c.get("vid_url")]
        else:
            all_characters = [c for c in all_characters if c.get("img_url")]

        # Pagination
        characters = all_characters[offset:offset + 50]
        next_offset = str(offset + len(characters)) if len(characters) == 50 else None

        results = []
        for char in characters:
            if not all(k in char for k in ["id", "name", "anime", "rarity"]):
                continue

            if user:
                count = sum(1 for c in user.get("characters", []) if c.get("id") == char["id"])
                caption = (
                    f"<b>👤 {escape(user.get('first_name', 'User'))}'s Collection:</b>\n"
                    f"🌸 <b>{escape(char['name'])} (x{count})</b>\n"
                    f"<b>🏖️ From: {escape(char['anime'])}</b>\n"
                    f"<b>🔮 Rarity: {escape(char['rarity'])}</b>\n"
                    f"<b>🆔 <code>{escape(str(char['id']))}</code></b>\n"
                )
            else:
                caption = (
                    f"<b>Character Details:</b>\n\n"
                    f"🌸 <b>{escape(char['name'])}</b>\n"
                    f"<b>🏖️ From: {escape(char['anime'])}</b>\n"
                    f"<b>🔮 Rarity: {escape(char['rarity'])}</b>\n"
                    f"<b>🆔 <code>{escape(str(char['id']))}</code></b>\n"
                )

            if char.get("vid_url"):
                results.append(InlineQueryResultVideo(
                    id=f"{char['id']}_{time.time()}",
                    video_url=char["vid_url"],
                    mime_type="video/mp4",
                    thumbnail_url=char.get("thum_url", "https://example.com/default.jpg"),
                    title=char["name"],
                    description=f"{char['anime']} | {char['rarity']}",
                    caption=caption,
                    parse_mode="HTML"
                ))
            elif char.get("img_url"):
                results.append(InlineQueryResultPhoto(
                    id=f"{char['id']}_{time.time()}",
                    photo_url=char["img_url"],
                    thumbnail_url=char["img_url"],
                    caption=caption,
                    parse_mode="HTML"
                ))

        await query.answer(results, cache_time=1, next_offset=next_offset)

    except Exception as e:
        print(f"Inline query error: {e}")
        await query.answer([], cache_time=1)