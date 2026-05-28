# =======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
# =======================================================

import os
import asyncio

from logging import getLogger

from motor.motor_asyncio import AsyncIOMotorClient
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

from pyrogram import filters, enums
from pyrogram.types import (
    ChatMemberUpdated,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)

from AviaxMusic import app
from config import MONGO_DB_URI

LOGGER = getLogger(__name__)

mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo["Wel_DB"]
welcomedb = db["welcome_toggle_system"]


# =======================================================
# DATABASE
# =======================================================

async def get_welcome(chat_id: int):
    data = await welcomedb.find_one({"chat_id": chat_id})
    if not data:
        return True
    return data.get("welcome", True)


async def enable_welcome(chat_id: int):
    await welcomedb.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome": True}},
        upsert=True
    )


async def disable_welcome(chat_id: int):
    await welcomedb.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome": False}},
        upsert=True
    )


# =======================================================
# TEMP STORAGE
# =======================================================

class temp:
    MELCOW = {}


# =======================================================
# IMAGE SYSTEM
# =======================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BG_PATH = os.path.join(BASE_DIR, "..", "..", "assets", "wel2.png")
FONT_PATH = os.path.join(BASE_DIR, "..", "..", "assets", "font2.ttf")
DEFAULT_PIC = os.path.join(BASE_DIR, "..", "..", "assets", "upic.png")

os.makedirs("downloads", exist_ok=True)


def circle(pfp, size=(720, 720), brightness_factor=1.4):

    pfp = pfp.resize(size).convert("RGBA")
    pfp = ImageEnhance.Brightness(pfp).enhance(brightness_factor)

    mask = Image.new("L", size, 0)

    draw = ImageDraw.Draw(mask)

    draw.ellipse((0, 0, size[0], size[1]), fill=255)

    pfp.putalpha(mask)

    return pfp


def welcomepic(pic, user, chatname, user_id, uname):

    # ================= BACKGROUND ================= #

    try:
        if os.path.exists(BG_PATH):
            background = Image.open(BG_PATH).convert("RGBA")
        else:
            LOGGER.warning("wel2.png not found, using fallback background")
            background = Image.new(
                "RGBA",
                (2560, 1600),
                (25, 25, 25, 255)
            )

    except Exception as e:
        LOGGER.error(f"Background Error: {e}")

        background = Image.new(
            "RGBA",
            (2560, 1600),
            (25, 25, 25, 255)
        )

    # ================= PROFILE PIC ================= #

    try:

        if not pic or not os.path.exists(pic):
            pic = DEFAULT_PIC

        pfp = Image.open(pic).convert("RGBA")

    except Exception as e:

        LOGGER.error(f"Profile Error: {e}")

        pfp = Image.open(DEFAULT_PIC).convert("RGBA")

    pfp = circle(pfp)

    background.paste(pfp, (520, 420), pfp)

    # ================= DRAW ================= #

    draw = ImageDraw.Draw(background)

    try:

        font_id = ImageFont.truetype(FONT_PATH, 100)
        font_username = ImageFont.truetype(FONT_PATH, 100)
        font_name = ImageFont.truetype(FONT_PATH, 120)

    except:

        font_id = ImageFont.load_default()
        font_username = ImageFont.load_default()
        font_name = ImageFont.load_default()

    username_text = f"@{uname}" if uname else "No Username"

    # NAME
    draw.text(
        (1550, 1180),
        str(user)[:15],
        font=font_name,
        fill="#ffffff"
    )

    # ID
    draw.text(
        (1920, 1340),
        str(user_id),
        font=font_id,
        fill="#ffffff"
    )

    # USERNAME
    draw.text(
        (1920, 1480),
        username_text,
        font=font_username,
        fill="#ffffff"
    )

    # ================= SAVE ================= #

    output_path = f"downloads/welcome_{user_id}.png"

    background.save(output_path)

    return output_path


# =======================================================
# WELCOME COMMAND
# =======================================================

@app.on_message(filters.command("welcome") & filters.group)
async def welcome_cmd(_, message: Message):

    chat = message.chat
    chat_id = chat.id

    user = await app.get_chat_member(
        chat_id,
        message.from_user.id
    )

    if user.status not in (
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.OWNER
    ):
        return await message.reply_text(
            "**» ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ʜᴀɴᴅʟᴇ ᴡᴇʟᴄᴏᴍᴇ ꜱʏꜱᴛᴇᴍ**"
        )

    state = await get_welcome(chat_id)

    status = "ᴇɴᴀʙʟᴇᴅ" if state else "ᴅɪꜱᴀʙʟᴇᴅ"

    btn = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "ᴇɴᴀʙʟᴇ",
                    callback_data=f"wlc_on_{chat_id}"
                ),
                InlineKeyboardButton(
                    "ᴅɪꜱᴀʙʟᴇ",
                    callback_data=f"wlc_off_{chat_id}"
                )
            ]
        ]
    )

    await message.reply_text(
        f"» ᴄᴜʀʀᴇɴᴛʟʏ ᴡᴇʟᴄᴏᴍᴇ ꜱᴛᴀᴛᴜꜱ **{status}** ɪɴ **{chat.title}**",
        reply_markup=btn
    )


# =======================================================
# CALLBACK
# =======================================================

@app.on_callback_query(filters.regex("^wlc_"))
async def welcome_toggle(_, query):

    data = query.data.split("_")

    action = data[1]
    chat_id = int(data[2])

    member = await app.get_chat_member(
        chat_id,
        query.from_user.id
    )

    if member.status not in (
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.OWNER
    ):
        return await query.answer(
            "ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ 🥺",
            show_alert=True
        )

    if action == "on":
        await enable_welcome(chat_id)
        new_status = "ᴇɴᴀʙʟᴇᴅ"
    else:
        await disable_welcome(chat_id)
        new_status = "ᴅɪꜱᴀʙʟᴇᴅ"

    chat = await app.get_chat(chat_id)

    await query.message.edit_text(
        f"» ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ **{new_status}** ɪɴ **{chat.title}**"
    )

    await query.answer()


# =======================================================
# AUTO WELCOME
# =======================================================

@app.on_chat_member_updated(filters.group, group=-3)
async def greet_new_member(_, member: ChatMemberUpdated):

    try:

        chat_id = member.chat.id

        is_enabled = await get_welcome(chat_id)

        if not is_enabled:
            return

        if (
            member.new_chat_member
            and member.new_chat_member.status
            == enums.ChatMemberStatus.MEMBER
        ):

            user = member.new_chat_member.user

            if user.is_bot:
                return

            # ================= DOWNLOAD PROFILE ================= #

            try:

                if user.photo:
                    pic = await app.download_media(
                        user.photo.big_file_id,
                        file_name=f"downloads/{user.id}.png"
                    )
                else:
                    pic = DEFAULT_PIC

            except Exception as e:

                LOGGER.error(f"Photo Download Error: {e}")

                pic = DEFAULT_PIC

            # ================= DELETE OLD ================= #

            old = temp.MELCOW.get(f"welcome-{chat_id}")

            if old:
                try:
                    await old.delete()
                except:
                    pass

            # ================= CREATE IMAGE ================= #

            welcomeimg = welcomepic(
                pic,
                user.first_name,
                member.chat.title,
                user.id,
                user.username
            )

            username = (
                f"@{user.username}"
                if user.username
                else "No Username"
            )

            # ================= SEND MESSAGE ================= #

            msg = await app.send_photo(
                chat_id,
                photo=welcomeimg,
                caption=f"""
**⏤͟͟͞͞★ ʜᴇʟʟᴏ ᴅᴇᴀʀ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ : {member.chat.title}**

<u>**❖ ᴜsᴇʀ sʜᴏʀᴛ ɪɴғᴏ**</u>

**➻ ɴᴀᴍᴇ »** {user.mention}
**➻ ᴄʜᴀᴛ_ɪᴅ »** `{user.id}`
**➻ ᴜ_ɴᴀᴍᴇ »** {username}

**➻ ᴛʜᴀɴᴋs ғᴏʀ ᴊᴏɪɴɪɴɢ ᴜs ⚡️~!**
""",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "⊚ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⊚",
                                url=f"https://t.me/{app.username}?startgroup=true"
                            )
                        ]
                    ]
                )
            )

            temp.MELCOW[f"welcome-{chat_id}"] = msg

            # ================= AUTO DELETE ================= #

            async def delete_welcome():

                await asyncio.sleep(10)

                try:

                    await msg.delete()

                    if f"welcome-{chat_id}" in temp.MELCOW:
                        del temp.MELCOW[f"welcome-{chat_id}"]

                except:
                    pass

            asyncio.create_task(delete_welcome())

    except Exception as e:
        LOGGER.error(f"Welcome System Error: {e}")
