
from pyrogram import filters, enums
from AviaxMusic import app
from AviaxMusic.misc import SUDOERS


def _extract_custom_emojis(msg):
    emojis = []

    def _collect(text, entities):
        if not text or not entities:
            return
        for ent in entities:
            etype = ent.type
            if hasattr(etype, "value"):
                is_custom = etype == enums.MessageEntityType.CUSTOM_EMOJI
            else:
                is_custom = etype == "custom_emoji"
            eid = getattr(ent, "custom_emoji_id", None)
            if is_custom and eid:
                emoji = text[ent.offset: ent.offset + ent.length]
                emojis.append((emoji, eid))

    _collect(getattr(msg, "text", None), getattr(msg, "entities", None))
    _collect(getattr(msg, "caption", None), getattr(msg, "caption_entities", None))
    return emojis


def _extract_button_custom_emojis(msg):
    emojis = []
    markup = getattr(msg, "reply_markup", None)
    keyboard = getattr(markup, "inline_keyboard", None)
    if not keyboard:
        return emojis

    for row in keyboard:
        for btn in row:
            text = getattr(btn, "text", None)
            entities = getattr(btn, "text_entities", None) or getattr(btn, "entities", None)

            if text and entities:
                for ent in entities:
                    etype = ent.type
                    if hasattr(etype, "value"):
                        is_custom = etype == enums.MessageEntityType.CUSTOM_EMOJI
                    else:
                        is_custom = etype == "custom_emoji"
                    eid = getattr(ent, "custom_emoji_id", None)
                    if is_custom and eid:
                        emoji = text[ent.offset: ent.offset + ent.length]
                        emojis.append((emoji, eid))

            icon_id = getattr(btn, "icon_custom_emoji_id", None)
            if icon_id:
                label = text or ""
                emojis.append((label, icon_id))

    return emojis


@app.on_message(filters.command(["emojiid", "eid"], ["/", "!", "."]))
async def emoji_id_handler(client, message):
    if not message.from_user or message.from_user.id not in SUDOERS:
        return

    target = message.reply_to_message or message
    emojis = _extract_custom_emojis(target)
    if not emojis:
        return await message.reply_text("No premium/custom emojis found in this message.")

    lines = [f"{i}. {e} → <code>{eid}</code>" for i, (e, eid) in enumerate(emojis, start=1)]
    txt = "<b>Premium Emoji IDs:</b>\n\n" + "\n".join(lines)
    await message.reply_text(txt)


@app.on_message(filters.command(["buttonemojiid", "beid"], ["/", "!", "."]))
async def button_emoji_id_handler(client, message):
    if not message.from_user or message.from_user.id not in SUDOERS:
        return

    target = message.reply_to_message or message
    emojis = _extract_button_custom_emojis(target)
    if not emojis:
        return await message.reply_text("No premium/custom emojis found in inline buttons of this message.")

    lines = [f"{i}. {e} → <code>{eid}</code>" for i, (e, eid) in enumerate(emojis, start=1)]
    txt = "<b>Button Premium Emoji IDs:</b>\n\n" + "\n".join(lines)
    await message.reply_text(txt)


@app.on_message(filters.command(["msgeid", "meid"], ["/", "!", "."]))
async def message_id_emoji_handler(client, message):
    if not message.from_user or message.from_user.id not in SUDOERS:
        return

    if len(message.command) < 2:
        return await message.reply_text("Give a message ID. Usage: /msgeid <message_id>")

    try:
        msg_id = int(message.command[1])
    except Exception:
        return await message.reply_text("Invalid message ID.")

    try:
        target = await client.get_messages(message.chat.id, msg_id)
    except Exception:
        return await message.reply_text("Failed to fetch that message.")

    emojis = _extract_custom_emojis(target)
    if not emojis:
        return await message.reply_text("No premium/custom emojis found in that message.")

    lines = [f"{i}. {e} → <code>{eid}</code>" for i, (e, eid) in enumerate(emojis, start=1)]
    txt = "<b>Premium Emoji IDs (from message):</b>\n\n" + "\n".join(lines)
    await message.reply_text(txt)


@app.on_message(filters.command(["emojipack", "epack"], ["/", "!", "."]))
async def emoji_pack_handler(client, message):
    if not message.from_user or message.from_user.id not in SUDOERS:
        return

    target = message.reply_to_message or message
    raw_id = None

    if len(message.command) >= 2:
        raw_id = message.command[1].strip()
    else:
        emojis = _extract_custom_emojis(target)
        if emojis:
            _, raw_id = emojis[0]

    if raw_id is None:
        return await message.reply_text("Reply to a premium emoji or pass its ID.")

    try:
        cid = int(raw_id)
    except Exception:
        return await message.reply_text("Invalid custom emoji ID.")

    try:
        stickers = await client.get_custom_emoji_stickers([cid])
    except Exception as e:
        return await message.reply_text(f"Failed to fetch emoji pack info: <code>{e}</code>")

    if not stickers:
        return await message.reply_text("No emoji data found.")

    sticker = stickers[0]
    set_name = getattr(sticker, "set_name", None)

    if not set_name:
        return await message.reply_text("This emoji does not belong to a public pack.")

    link = f"https://t.me/addemoji/{set_name}"
    txt = (
        "<b>Emoji Pack:</b>\n\n"
        f"ID: <code>{cid}</code>\n"
        f"Name: <code>{set_name}</code>\n"
        f'<a href="{link}">Open Pack</a>'
    )
    await message.reply_text(txt, disable_web_page_preview=True)
