import os
import discord
from discord import app_commands
from discord.ext import commands
from keep_alive import keep_alive

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()

# Botの準備
bot = commands.Bot(command_prefix='!', intents=intents)

# Botが起動したときのイベント
@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')
    check_members.start()
    await send_update_message()
    await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name='ことり鯖'))


async def send_update_message():
    channel_id = 1295239928807948411
    channel = await bot.fetch_channel(channel_id)
    embed = discord.Embed(
        title="BOTが起動しました！",
        description="BOT has been started!",
        color=0x00BFFF,
        timestamp=datetime.now()
    )
    await channel.send(embed=embed)

try:
    keep_alive()
    bot.run(TOKEN)
except Exception as e:
    print(f'エラーが発生しました: {e}')
