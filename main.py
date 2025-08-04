# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import re
import sys
import json
import time
import asyncio
import requests
import subprocess

import core as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN)

@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(f"<b>Hello {m.from_user.mention} 👋\n\n I Am A Bot For Downloading Links From Your **.TXT** File And Uploading On Telegram. First, Send Me /upload Command And Follow The Steps..\n\nUse /stop to stop any ongoing task.</b>")

@bot.on_message(filters.command("stop"))
async def restart_handler(_, m):
    await m.reply_text("**Stopped**🚦", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    editable = await m.reply_text('Send TXT file ⚡️')
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await input.delete(True)

    try:
        with open(x, "r") as f:
            content = f.read().split("\n")
        links = [i for i in content if i.strip()]
        os.remove(x)
    except:
        await m.reply_text("**Invalid file input.**")
        os.remove(x)
        return

    await editable.edit(f"**Total Links Found 🔗:** {len(links)}\nSend The Starting Point (Default: 1)")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)

    await editable.edit("**Now Send Your Batch Name**")
    input1: Message = await bot.listen(editable.chat.id)
    batch_name = input1.text
    await input1.delete(True)

    await editable.edit("**Enter Resolution 📸** (144, 240, 360, 480, 720, 1080)")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)

    resolution_map = {"144": "256x144", "240": "426x240", "360": "640x360", "480": "854x480", "720": "1280x720", "1080": "1920x1080"}
    res = resolution_map.get(raw_text2, "UN")

    await editable.edit("Enter Caption For Your Uploaded File")
    input3: Message = await bot.listen(editable.chat.id)
    caption = input3.text
    await input3.delete(True)

    await editable.edit("Send The Thumbnail URL\nExample: https://graph.org/file/sample.jpg\nOr Type 'no' To Skip")
    input6 = await bot.listen(editable.chat.id)
    thumb_url = input6.text
    await input6.delete(True)
    await editable.delete()

    thumb = None
    if thumb_url.lower() != "no":
        status, _ = getstatusoutput(f"wget '{thumb_url}' -O 'thumb.jpg'")
        if status == 0:
            thumb = "thumb.jpg"

    start_count = int(raw_text) if raw_text.isdigit() else 1

    try:
        for i in range(start_count - 1, len(links)):
            link = links[i].strip()
            if not link.startswith("http"):
                continue
            
            if "drive.google.com" in link:
                link = f"https://drive.google.com/uc?export=download&id={link.split('/')[-2]}"

            name = f'{str(i+1).zfill(3)}_{re.sub(r"[^\w\s]", "", link.split("/")[-1])[:60]}.mp4'

            if "youtu" in link:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"

            cmd = f'yt-dlp -f "{ytf}" "{link}" -o "{name}" --merge-output-format mp4'
            progress_msg = await m.reply_text(f"**Downloading ⬇️...**\n**Name:** `{name}`\n**Quality:** {raw_text2}\n**URL:** `{link}`")

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                await m.reply_text(f"**Download Failed 🚨**\n{result.stderr}")
                continue
            
            caption_text = f"**🎥 Video ID:** {str(i+1).zfill(3)}\n**📁 Batch:** {batch_name}\n\n{caption}"
            await bot.send_video(m.chat.id, video=name, caption=caption_text, thumb=thumb)
            os.remove(name)
            await progress_msg.delete()
            await asyncio.sleep(1)

    except FloodWait as e:
        await m.reply_text(f"**Rate Limit Exceeded! ⏳ Waiting {e.value} Seconds...**")
        await asyncio.sleep(e.value)

    except Exception as e:
        await m.reply_text(f"**Error Occurred 🚨**\n{str(e)}")

    await m.reply_text("**✅ Task Completed!**")

bot.run()
