import time
import random
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from AloneX import app
from AloneX.misc import SPECIAL_ID, _boot_
from AloneX.plugins.sudo.sudoers import sudoers_list
from AloneX.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from AloneX.utils.decorators.language import LanguageStart
from AloneX.utils.formatters import get_readable_time
from AloneX.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string
from pyrogram.errors import RPCError

VALID_EMOJII = ["🔥", "💋", "🥺", "😒", "💖",
                "💘", "💕", "✨", "🥰", "🍌", "💔",
                "😓", "🫧"]


async def send_image_or_fallback(client, chat_id, photo, caption, reply_markup=None, disable_web_page_preview=True):
    """Try to send a photo from `photo` (URL or file). If Telegram rejects it as WEBPAGE_MEDIA_EMPTY
    or any other RPCError, fall back to sending a plain message with the caption so the bot doesn't crash.

    Returns the message object sent.
    """
    try:
        return await client.send_photo(chat_id=chat_id, photo=photo, caption=caption, reply_markup=reply_markup)
    except RPCError as e:
        # Telegram sometimes returns WEBPAGE_MEDIA_EMPTY when the URL is not a direct image.
        # Fall back to sending a text message so users still see the content.
        try:
            return await client.send_message(chat_id=chat_id, text=caption, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview)
        except Exception as ex:
            # Last-resort: print and raise so the log shows it; but avoid crashing the handler.
            print(f"Failed to send fallback message: {ex}")
            return None


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name.startswith("help"):
            keyboard = help_pannel(_)
            caption = _["help_1"].format(config.SUPPORT_CHAT)
            return await send_image_or_fallback(client=client, chat_id=message.chat.id, photo=config.START_IMG_URL, caption=caption, reply_markup=keyboard)

        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                )
            return

        if name.startswith("inf"):
            m = await message.reply_text("🔎")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                    ],
                ]
            )
            await m.delete()
            # Use helper that falls back when thumbnail URL is not a direct image
            await send_image_or_fallback(client=app, chat_id=message.chat.id, photo=thumbnail, caption=searched_text, reply_markup=key)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                )
    else:
        out = private_panel(_)
        caption = _["start_2"].format(message.from_user.mention, app.mention)
        await send_image_or_fallback(client=client, chat_id=message.chat.id, photo=config.START_IMG_URL, caption=caption, reply_markup=InlineKeyboardMarkup(out))
        if await is_on_off(2):
            return await app.send_message(
                chat_id=config.LOGGER_ID,
                text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
            )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    caption = _["start_1"].format(app.mention, get_readable_time(uptime))
    await send_image_or_fallback(client=client, chat_id=message.chat.id, photo=config.START_IMG_URL, caption=caption, reply_markup=InlineKeyboardMarkup(out))
    return await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                caption = _["start_3"].format(
                    message.from_user.first_name,
                    app.mention,
                    message.chat.title,
                    app.mention,
                )
                await send_image_or_fallback(client=client, chat_id=message.chat.id, photo=config.START_IMG_URL, caption=caption, reply_markup=InlineKeyboardMarkup(out))
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)
