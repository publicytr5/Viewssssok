import os
import asyncio
import random
from datetime import datetime
from threading import Thread
from flask import Flask
from pyrogram import Client, errors

app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is active and running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host='0.0.0.0', port=port)

# Environment Variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")

# ফায়ার, শুভেচ্ছা, লাভ এবং থাম্বস আপ ইমোজি
EMOJIS = ["🔥", "🎉", "❤️", "👍"]

tg_app = Client("render_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

daily_reactions_count = 0
current_day = datetime.now().day

async def auto_view_and_react():
    global daily_reactions_count, current_day
    
    await tg_app.start()
    print(">>> Telegram Client Started Successfully! <<<")

    while True:
        try:
            today = datetime.now().day
            if today != current_day:
                daily_reactions_count = 0
                current_day = today
                print("নতুন দিন শুরু, রিয়েকশন কাউন্টার রিসেট করা হলো।")

            try:
                chat = await tg_app.get_chat(TARGET_CHANNEL)
                channel_id = chat.id
            except Exception as e:
                print(f"চ্যানেল খুঁজে পাওয়া যাচ্ছে না! TARGET_CHANNEL ঠিক আছে তো? Error: {e}")
                await asyncio.sleep(60)
                continue

            messages = []
            async for msg in tg_app.get_chat_history(channel_id, limit=15):
                messages.append(msg)

            if messages:
                # ১. ভিউ মার্ক করা
                msg_ids = [m.id for m in messages]
                await tg_app.read_conversation_history(channel_id, max_id=max(msg_ids))
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {len(msg_ids)} টি পোস্টে ভিউ দেওয়া হয়েছে।")

                # ২. রিয়েকশন দেওয়া (🔥, 🎉, ❤️, 👍)
                if daily_reactions_count < 150:
                    react_limit = min(random.randint(1, 2), len(messages))
                    selected_messages = random.sample(messages, react_limit)

                    for msg in selected_messages:
                        if daily_reactions_count >= 150:
                            break
                        
                        emoji = random.choice(EMOJIS)
                        try:
                            await tg_app.send_reaction(channel_id, msg.id, emoji)
                            daily_reactions_count += 1
                            print(f"Post ID {msg.id} -> {emoji} | আজকের মোট: {daily_reactions_count}")
                        except errors.FloodWait as e:
                            print(f"FloodWait: {e.value} সেকেন্ড অপেক্ষা করতে হবে...")
                            await asyncio.sleep(e.value)
                        except Exception as e:
                            print(f"Reaction Error (Post {msg.id}): {e}")
                        
                        await asyncio.sleep(random.randint(10, 20))

        except Exception as e:
            print(f"প্রধান লুপে এরর: {e}")

        # ৩-৫ মিনিট পর পর নতুন পোস্ট চেক
        sleep_time = random.randint(180, 300)
        print(f"পরবর্তী চেকের জন্য {sleep_time // 60} মিনিট অপেক্ষা করা হচ্ছে...\n")
        await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    asyncio.run(auto_view_and_react())
