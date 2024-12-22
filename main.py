import os
import discord
import re
import sys
from discord import app_commands
from discord.ext import commands
from keep_alive import keep_alive
from datetime import datetime, timedelta


TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()

# Botの準備
bot = commands.Bot(command_prefix='!', intents=intents)

ALLOWED_USERS = [1212687868603007067,1212161927405637712]

# Botが起動したときのイベント
@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')
    await send_update_message()
    await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name='ことり鯖'))

@bot.event
async def on_message(message):
    message_content = message.content
    message_id = message.id
    guild = message.guild
    channel = message.channel
    if channel.name is None:
        return
    else:
        channel_name = channel.name
        channel_id = channel.id
    user = message.author
    user_id = user.id
    user_name = user.name
    user_avatar = user.avatar
    server_id = message.guild.id
    file = message.attachments
    file_url = file[0].url if file else None
    message_embeds = message.embeds

    message_link_pattern = re.compile(r'https://discord.com/channels/(\d+)/(\d+)/(\d+)')
    match = message_link_pattern.search(message.content)

    if match:
        server_id = int(match.group(1))
        channel_id = int(match.group(2))
        message_id = int(match.group(3))

        guild = bot.get_guild(server_id)
        if guild:
            channel = guild.get_channel(channel_id)
            if channel:
                try:
                    target_message = await channel.fetch_message(message_id)
                    message_link = f"https://discord.com/channels/{server_id}/{channel_id}/{message_id}"

                    embed = discord.Embed(
                        description=f"{target_message.content}\nFrom {channel.mention}",
                        color=discord.Color.blue(),
                        timestamp=target_message.created_at
                    )
                    author_avatar_url = target_message.author.display_avatar.url
                    embed.set_author(name=target_message.author.display_name, icon_url=author_avatar_url)

                    for attachment in target_message.attachments:
                        embed.set_image(url=attachment.url)

                    button = discord.ui.Button(label="メッセージ先はこちら", url=message_link)
                    view = discord.ui.View()
                    view.add_item(button)

                    content_file = target_message.attachments
                    content_file_url = content_file[0].url if content_file else None

                    await message.channel.send(embed=embed, view=view)

                    # ファイルをダウンロードして添付する処理
                    if content_file_url:
                        picture_extensions = ['png', 'jpg', 'jpeg', 'gif', 'webp']

                        # ファイルが画像以外の場合に添付
                        if not any(content_file_url.endswith(ext) for ext in picture_extensions):
                            async with aiohttp.ClientSession() as session:
                                async with session.get(content_file_url) as response:
                                    if response.status == 200:
                                        file_data = await response.read()
                                        file_name = content_file[0].filename  # 元のファイル名を取得

                                        # ファイルを一時保存して送信
                                        with open(file_name, 'wb') as f:
                                            f.write(file_data)

                                        await message.channel.send(file=discord.File(file_name))

                                        # 一時ファイルを削除
                                        os.remove(file_name)
                                    else:
                                        await message.channel.send('ファイルのダウンロードに失敗しました。')

                    else:
                        print('ファイルが添付されていません。')

                except discord.NotFound:
                    await message.channel.send('メッセージが見つかりませんでした。')
                except discord.Forbidden:
                    await message.channel.send('メッセージを表示する権限がありません。')
                except discord.HTTPException as e:
                    await message.channel.send(f'メッセージの取得に失敗しました: {e}')

    if message.content == "kotori!bot stop":
        if server_id == 1275631726206386297:
            if user_id == 1212687868603007067:
                embed = discord.Embed(title='BOTが停止しました^^',
                description="なるはやで起動させてください。",
                color=0xff0000,
                timestamp=datetime.utcnow(),
                )
                await message.channel.send(embed=embed)
                sys.exit()
            else:
                await message.channel.send("あなたにはこの操作を行う権限がありません。")
    # 「r!test」が送信された場合に「あ」と返す
    elif message.content == "b!test" or message.content == "kotori!test":
        await message.channel.send("GitHubで起動されています")
    # 「r!vsc」が送信された場合にvscのリンクを返す
    elif message.content == "kotori!vsc":
        if user_id == 1212687868603007067:
            await message.channel.send("https://vscode.dev/github/kotori-server/kotori-server-bot?vscode-lang=ja")
    elif message.content == "kotori!link":
        await message.channel.send("https://github.com/fynk7777/kotori-server-bot")

    if isinstance(message.channel, discord.TextChannel) and message.channel.is_news():
        # メッセージを公開
        await message.publish()

    if user_id == 1295240136564408350:
        if channel_id == 1295239928807948411:
            sys.exit()

@bot.tree.command(name="status",description="ステータスを設定するコマンドです")
@app_commands.describe(text="ステータスを設定します")
async def text(interaction: discord.Interaction, text: str):
    if interaction.user.id in ALLOWED_USERS:
        await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name=f'{text}'))
        await interaction.response.send_message(f'ステータスを「{text}」に設定しました。',ephemeral=True)
    else:
        await interaction.response.send_message('このコマンドを実行する権限がありません。', ephemeral=True)

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