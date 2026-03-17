import random
import string
import requests

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from AviaxMusic import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app
from AviaxMusic.core.call import Aviax
from AviaxMusic.utils import seconds_to_min, time_to_seconds
from AviaxMusic.utils.channelplay import get_channeplayCB
from AviaxMusic.utils.decorators.language import languageCB
from AviaxMusic.utils.decorators.play import PlayWrapper
from AviaxMusic.utils.formatters import formats
from AviaxMusic.utils.inline import (
    botplaylist_markup,
    livestream_markup,
    playlist_markup,
    slider_markup,
    track_markup,
)
from AviaxMusic.utils.logger import play_logs
from AviaxMusic.utils.stream.stream import stream
from config import BANNED_USERS, lyrical


# ✅ SAFE THUMB FUNCTION
def safe_thumb(thumb):
    if not thumb:
        return "https://telegra.ph/file/2b3c0c5d5f8c1a2e3d4f5.jpg"
    return thumb


async def send_photo_safe(message, photo_url, caption, markup):
    try:
        photo_url = safe_thumb(photo_url)
        res = requests.get(photo_url, timeout=10)

        with open("thumb.jpg", "wb") as f:
            f.write(res.content)

        return await message.reply_photo(
            photo="thumb.jpg",
            caption=caption,
            reply_markup=markup,
        )
    except Exception as e:
        print("Thumbnail Error:", e)
        return await message.reply_text(
            caption,
            reply_markup=markup,
        )


@app.on_message(
    filters.command(
        [
            "play",
            "vplay",
            "cplay",
            "cvplay",
            "playforce",
            "vplayforce",
            "cplayforce",
            "cvplayforce",
        ]
    )
    & filters.group
    & ~BANNED_USERS
)
@PlayWrapper
async def play_commnd(
    client,
    message: Message,
    _,
    chat_id,
    video,
    channel,
    playmode,
    url,
    fplay,
):
    mystic = await message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )

    # 👉 (बाकी code same रहेगा ऊपर का — कोई change नहीं)

    # 🔥 FINAL PARTS FIXED BELOW

    if str(playmode) != "Direct":
        if plist_type:
            ran_hash = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=10)
            )
            lyrical[ran_hash] = plist_id
            buttons = playlist_markup(
                _,
                ran_hash,
                message.from_user.id,
                plist_type,
                "c" if channel else "g",
                "f" if fplay else "d",
            )
            await mystic.delete()

            return await send_photo_safe(
                message,
                img,
                cap,
                InlineKeyboardMarkup(buttons),
            )

        else:
            if slider:
                buttons = slider_markup(
                    _,
                    track_id,
                    message.from_user.id,
                    query,
                    0,
                    "c" if channel else "g",
                    "f" if fplay else "d",
                )
                await mystic.delete()

                return await send_photo_safe(
                    message,
                    details.get("thumb"),
                    _["play_10"].format(
                        details["title"].title(),
                        details["duration_min"],
                    ),
                    InlineKeyboardMarkup(buttons),
                )

            else:
                buttons = track_markup(
                    _,
                    track_id,
                    message.from_user.id,
                    "c" if channel else "g",
                    "f" if fplay else "d",
                )
                await mystic.delete()

                return await send_photo_safe(
                    message,
                    img,
                    cap,
                    InlineKeyboardMarkup(buttons),
                )
