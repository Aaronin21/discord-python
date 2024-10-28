import asyncio
import os
import discord
import requests

# Ensure your environment variables are set correctly on Replit
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

if not TOKEN or not CHANNEL_ID:
    print("Environment variables DISCORD_TOKEN and CHANNEL_ID must be set.")
    exit(1)

BOORU_API_URL = "https://e621.net/posts.json"
TAG = "femboy"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_post_id = None

async def fetch_new_booru_post():
    global last_post_id
    try:
        headers = {"User-Agent": "DiscordBot (your-email@example.com)"}
        response = requests.get(BOORU_API_URL, headers=headers, params={"tags": TAG, "limit": 1})
        data = response.json().get("posts", [])
        if data:
            latest_post = data[0]
            latest_post_id = latest_post.get("id")
            if latest_post_id != last_post_id:
                last_post_id = latest_post_id
                return latest_post
    except Exception as e:
        print(f"Error fetching booru post: {e}")
    return None

async def download_file(url):
    try:
        response = requests.get(url)
        file_name = url.split("/")[-1]
        with open(file_name, 'wb') as file:
            file.write(response.content)
        return file_name
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')
    await post_updates()

async def post_updates():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    while not client.is_closed():
        new_post = await fetch_new_booru_post()
        if new_post:
            post_url = f"https://e621.net/posts/{new_post['id']}"
            image_url = new_post.get("file", {}).get("url")
            if image_url:
                file_name = await download_file(image_url)
                if file_name:
                    await channel.send(content=f"New post with tag '{TAG}': {post_url}", file=discord.File(file_name))
                    os.remove(file_name)
            else:
                await channel.send(content=f"New post with tag '{TAG}': {post_url} (No image available)")
        await asyncio.sleep(300)
    
client.run(TOKEN)
