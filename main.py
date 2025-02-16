# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import re
import sys
import time
import asyncio
import requests
from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput
from pyrogram import Client, filters
from pyrogram.types import Message

# Load API credentials from environment variables
API_ID = int(os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(
        f"<b>Hello {m.from_user.mention} 👋\n\n"
        "I am a bot for downloading links from your **.TXT** file "
        "and then uploading the extracted files on Telegram.\n\n"
        "To use me, send the `/upload` command and follow the steps.</b>"
    )

@bot.on_message(filters.command("stop"))
async def stop(bot: Client, m: Message):
    await m.reply_text("**Bot Stopped 🚦**")
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    editable = await m.reply_text("Send your `.txt` file containing links ⚡️")
    input_msg = await bot.listen(editable.chat.id)

    if not input_msg.document:
        await editable.edit("**Please send a valid `.txt` file** ❌")
        return

    file_path = await input_msg.download()
    await input_msg.delete()

    try:
        with open(file_path, "r") as f:
            content = f.read().splitlines()
        links = [line.strip() for line in content if line.strip()]
        os.remove(file_path)
    except Exception as e:
        await editable.edit(f"**Error in processing file:** `{str(e)}`")
        return

    if not links:
        await editable.edit("**No valid links found in the file!** ❌")
        return

    await editable.edit(
        f"**🔗 Total Links Found:** `{len(links)}`\n"
        "**Send the starting index (default is 1)**"
    )
    start_index = await bot.listen(editable.chat.id)
    try:
        start_index = int(start_index.text) - 1
    except ValueError:
        start_index = 0

    await editable.edit("**Send the batch name 📁**")
    batch_name = await bot.listen(editable.chat.id)
    batch_name = batch_name.text.strip()

    await editable.edit("**Select resolution (144, 240, 360, 480, 720, 1080)**")
    resolution_msg = await bot.listen(editable.chat.id)
    resolution = resolution_msg.text.strip()
    
    resolution_map = {
        "144": "256x144",
        "240": "426x240",
        "360": "640x360",
        "480": "854x480",
        "720": "1280x720",
        "1080": "1920x1080"
    }
    selected_res = resolution_map.get(resolution, "best")

    await editable.edit("**Enter a caption for uploaded files 📜**")
    caption_msg = await bot.listen(editable.chat.id)
    caption_text = caption_msg.text.strip()

    await editable.edit("**Send thumbnail URL (or type `no` to skip)**")
    thumb_msg = await bot.listen(editable.chat.id)
    thumbnail_url = thumb_msg.text.strip()

    if thumbnail_url.lower() != "no":
        getstatusoutput(f"wget '{thumbnail_url}' -O 'thumb.jpg'")
        thumbnail_path = "thumb.jpg"
    else:
        thumbnail_path = None

    await editable.delete()
    
    for index, link in enumerate(links[start_index:], start=start_index + 1):
        link = link.strip()

        # Process different types of links
        if "drive.google.com" in link:
            link = link.replace("file/d/", "uc?export=download&id=").split("/view")[0]
        elif "youtu" in link:
            ytdl_format = f"b[height<={selected_res}][ext=mp4]/bv[height<={selected_res}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
        else:
            ytdl_format = f"b[height<={selected_res}]/bv[height<={selected_res}]+ba/b/bv+ba"

        file_name = f"{str(index).zfill(3)}) {batch_name}.mp4"
        file_caption = f"📽️ **{file_name}**\n📁 **Batch:** `{batch_name}`\n🔗 **Link:** `{link}`"

        # Determine if it's a video or a PDF
        if ".pdf" in link:
            file_name = f"{str(index).zfill(3)}) {batch_name}.pdf"
            file_caption = f"📁 **{file_name}**\n📁 **Batch:** `{batch_name}`"

            os.system(f'wget "{link}" -O "{file_name}"')
            await bot.send_document(m.chat.id, document=file_name, caption=file_caption)
            os.remove(file_name)
        else:
            cmd = f'yt-dlp -f "{ytdl_format}" "{link}" -o "{file_name}"'
            os.system(cmd)
            await bot.send_video(m.chat.id, video=file_name, caption=file_caption, thumb=thumbnail_path)
            os.remove(file_name)

        await asyncio.sleep(1)

    await m.reply_text("✅ **Upload Completed!**")

if __name__ == "__main__":
    bot.run()
    
