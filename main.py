# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
import os
import sys
import asyncio
import requests
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message

# Load API credentials
API_ID = int(os.getenv("API_ID", "24930837"))
API_HASH = os.getenv("API_HASH", "3ed76c228ff85f369d1b3f9cf77cc9f8")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7490925963:AAERORe7zOZrFoZ5Oq8deZvntiWkMXj22RM")

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(
        "👋 **Hello!** I can extract and download **videos and PDFs** from `.txt` files.\n"
        "Send `/upload` to begin!"
    )

@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    await m.reply_text("📂 **Send me a `.txt` file with links.**")
    
    input_msg = await bot.listen(m.chat.id)
    if not input_msg.document:
        await m.reply_text("❌ **Please send a valid `.txt` file.**")
        return
    
    file_path = await input_msg.download()
    await input_msg.delete()

    try:
        with open(file_path, "r") as f:
            links = [line.strip() for line in f if line.strip()]
        os.remove(file_path)
    except Exception as e:
        await m.reply_text(f"❌ **Error reading file:** `{str(e)}`")
        return

    if not links:
        await m.reply_text("❌ **No valid links found in the file.**")
        return

    await m.reply_text(f"✅ **{len(links)} links found. Processing...**")

    for index, link in enumerate(links, start=1):
        link = link.strip()
        file_name = f"file_{index}"

        if "youtube.com" in link or "youtu.be" in link:
            download_cmd = f'yt-dlp -f "best[ext=mp4]" -o "{file_name}.mp4" "{link}"'
        elif ".pdf" in link:
            download_cmd = f'wget "{link}" -O "{file_name}.pdf"'
        else:
            continue  

        os.system(download_cmd)

        if os.path.exists(f"{file_name}.mp4"):
            await bot.send_video(m.chat.id, video=f"{file_name}.mp4", caption=f"📽️ **Video {index}**")
            os.remove(f"{file_name}.mp4")
        elif os.path.exists(f"{file_name}.pdf"):
            await bot.send_document(m.chat.id, document=f"{file_name}.pdf", caption=f"📄 **PDF {index}**")
            os.remove(f"{file_name}.pdf")

    await m.reply_text("✅ **Upload Completed!**")

if __name__ == "__main__":
    bot.run()
        
