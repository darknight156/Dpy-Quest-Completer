import discord
from discord.ext import commands
from discord import ui
import sqlite3
import aiohttp
import asyncio
import base64
import json
import random
from uuid import uuid4
from datetime import datetime

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
    
bot.run('MTI4MTU4NzI0ODQyMDIyNTAyNQ.GD4Hf8.D4hClv4lcyoC2-x_k3g7_rzYv_C5fke75EXUhM')