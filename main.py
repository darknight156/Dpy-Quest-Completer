# Made By DarkNighT (- mmiiiuu)
# Made By DarkNighT (- mmiiiuu)
# Made By DarkNighT (- mmiiiuu)

import discord
from discord.ext import commands
import sqlite3

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


def init_db():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS token (user_id TEXT PRIMARY KEY, token TEXT NOT NULL)')
    conn.commit()
    conn.close()

init_db()

    
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.load_extension('cogs.token')
    await bot.load_extension('cogs.quest')
    await bot.load_extension('cogs.notifier')
    
bot.run('BOT-TOKEN')
