# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01    input1: Message = await bot.listen(editable.chat.id)
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
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN)

@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(f"<b>Hello {m.from_user.mention} 👋\n\n I Am A Bot For Download Links From Your **.TXT** File And Then Upload That File On Telegram.\nUse /stop to stop any ongoing task.</b>")

@bot.on_message(filters.command("stop"))
async def restart_handler(_, m: Message):
    await m.reply_text("**Stopped**🚦")
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    editable = await m.reply_text('Send a .txt file ⚡️')
    input_file: Message = await bot.listen(editable.chat.id)
    if input_file.document:
        file_path = await input_file.download()
        await input_file.delete()
    else:
        await m.reply_text("Invalid file input. Please send a .txt file.")
        return

    path = f"./downloads/{m.chat.id}"
    
    try:
        with open(file_path, "r") as f:
            content = f.read().splitlines()
        links = [i for i in content if "http" in i]
        os.remove(file_path)
    except Exception as e:
        await m.reply_text(f"Error reading file: {str(e)}")
        os.remove(file_path)
        return

    if not links:
        await m.reply_text("No valid links found in the file.")
        return

    await editable.edit(f"**Total Links Found: {len(links)}**\nSend the starting point (default: 1)")
    input_start: Message = await bot.listen(editable.chat.id)
    raw_text = input_start.text.strip()
    start_index = int(raw_text) if raw_text.isdigit() else 1
    await input_start.delete()
    
    await editable.edit("Now Please Send Me Your Batch Name")
    input_batch: Message = await bot.listen(editable.chat.id)
    batch_name = input_batch.text.strip()
    await input_batch.delete()
    
    await editable.edit("Enter resolution: 144, 240, 360, 480, 720, 1080")
    input_res: Message = await bot.listen(editable.chat.id)
    res_map = {"144": "256x144", "240": "426x240", "360": "640x360", "480": "854x480", "720": "1280x720", "1080": "1920x1080"}
    resolution = res_map.get(input_res.text.strip(), "UN")
    await input_res.delete()
    
    await editable.edit("Enter caption for uploaded files")
    input_caption: Message = await bot.listen(editable.chat.id)
    caption = input_caption.text.strip()
    await input_caption.delete()
    
    await editable.edit("Send thumbnail URL or type 'no' if you don't want a thumbnail")
    input_thumb: Message = await bot.listen(editable.chat.id)
    thumb_url = input_thumb.text.strip()
    await input_thumb.delete()
    
    if thumb_url.lower() != "no" and (thumb_url.startswith("http://") or thumb_url.startswith("https://")):
        getstatusoutput(f"wget '{thumb_url}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = None
    
    count = start_index
    
    for i in range(start_index - 1, len(links)):
        url = links[i]
        name = f"{str(count).zfill(3)}) Video {count}"  # Generate a basic name
        
        ytf = f"b[height<={resolution}][ext=mp4]" if "youtu" in url else f"b[height<={resolution}]"
        cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'
        
        try:
            prog = await m.reply_text(f"Downloading {name}... 📥")
            subprocess.run(cmd, shell=True)
            await bot.send_video(m.chat.id, f"{name}.mp4", caption=caption, thumb=thumb)
            count += 1
            os.remove(f"{name}.mp4")
            await prog.delete()
        except Exception as e:
            await m.reply_text(f"Error downloading {name}: {str(e)}")
            continue

    await m.reply_text("**Done Boss 😎**")

bot.run()
