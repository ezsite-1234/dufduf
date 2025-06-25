import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

user_settings = {}

@bot.event
async def on_ready():
    print(f"Bot起動: {bot.user}")
    try:
        await tree.sync()
    except Exception as e:
        print(f"コマンド同期エラー: {e}")

@tree.command(name="setup", description="セットアップします。セットアップには認証の為複雑な設定が必要になります。")
@app_commands.describe(message="送信するテキスト（改行可）", count="送信回数（1〜7）")
async def setup(interaction: discord.Interaction, message: str, count: int):
    if not (1 <= count <= 7):
        await interaction.response.send_message("回数は1〜7の間で指定してください。", ephemeral=True)
        return

    user_settings[interaction.user.id] = {
        "message": message,
        "count": count,
        "channel_id": interaction.channel.id
    }

    class StartView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="", style=discord.ButtonStyle.success, emoji="▶️")
        async def start(self, button: discord.ui.Button, interact: discord.Interaction):
            if interact.user.id != interaction.user.id:
                return  # 他人が押しても無視

            data = user_settings.get(interact.user.id)
            if data:
                channel = bot.get_channel(data["channel_id"])
                for _ in range(data["count"]):
                    await channel.send(data["message"])
                    await asyncio.sleep(1)
            # 応答なし（完全にsilent）

    view = StartView()
    await interaction.response.send_message(view=view, ephemeral=True)  # 完全に本人だけに表示

# FlaskによるWebサービス（Render用）
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

bot.run(TOKEN)
