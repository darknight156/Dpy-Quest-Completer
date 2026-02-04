# Made By DarkNighT (- mmiiiuu)
# Made By DarkNighT (- mmiiiuu)
# Made By DarkNighT (- mmiiiuu)

import discord
import sqlite3
import asyncio
import datetime
import json
import aiohttp
from discord import ui
from discord.ext import commands, tasks

from utils.header import get_headers

class QuestNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.known_quests = set() 
        self.check_new_quests.start()
        
    def cog_unload(self):
        self.check_new_quests.cancel()
    
    @tasks.loop(minutes=30)
    async def check_new_quests(self):
        """Check for new quests and notify users"""
        await self.bot.wait_until_ready()
        
        conn = sqlite3.connect('store.db')
        cursor = conn.execute('SELECT user_id, token, notify_channel FROM token WHERE notify_channel IS NOT NULL')
        users = cursor.fetchall()
        conn.close()
        
        if not users:
            return
        
        for user_id, token, channel_id in users:
            try:
                headers = get_headers(token)
                
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://discord.com/api/v9/quests/@me", headers=headers) as resp:
                        if resp.status != 200:
                            continue
                        
                        data = json.loads(await resp.text())
                        all_quests = data.get('quests', [])
                        
                        new_quests = []
                        for q in all_quests:
                            q_id = q.get('id')
                            if q_id == '1412491570820812933':
                                continue
                            
                            config = q.get('config', {})
                            
                            expires_at = config.get('expires_at') or config.get('expiresAt')
                            if expires_at:
                                try:
                                    expiry = datetime.datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                                    if datetime.datetime.now(expiry.tzinfo) > expiry:
                                        continue
                                except:
                                    pass
                            
                            user_status = q.get('user_status')
                            if user_status:
                                completed = user_status.get('completed_at') or user_status.get('completedAt')
                                if completed:
                                    continue
                            
                            if q_id not in self.known_quests:
                                new_quests.append(q)
                                self.known_quests.add(q_id)
                        
                        if new_quests:
                            channel = self.bot.get_channel(int(channel_id))
                            if channel:
                                await self.notify_new_quests(channel, new_quests)
                        
                        break 
                        
            except Exception as e:
                print(f"Error checking quests for user {user_id}: {e}")
                continue
    
    @check_new_quests.before_loop
    async def before_check_quests(self):
        """Initialize known quests before starting the loop"""
        await self.bot.wait_until_ready()
        
        conn = sqlite3.connect('store.db')
        cursor = conn.execute('SELECT token FROM token LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return
        
        token = row[0]
        headers = get_headers(token)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://discord.com/api/v9/quests/@me", headers=headers) as resp:
                    if resp.status == 200:
                        data = json.loads(await resp.text())
                        all_quests = data.get('quests', [])
                        
                        for q in all_quests:
                            q_id = q.get('id')
                            self.known_quests.add(q_id)
        except Exception as e:
            print(f"Error initializing known quests: {e}")
    
    async def notify_new_quests(self, channel, new_quests):
        """Send notification about new quests"""
        for quest in new_quests:
            q_id = quest.get('id')
            config = quest.get('config', {})
            messages = config.get('messages', {})
            
            quest_name = messages.get('quest_name') or messages.get('questName') or 'Unknown Quest'            
            
            expires_at = config.get('expires_at') or config.get('expiresAt')
            expiry_text = "Unknown"
            if expires_at:
                try:
                    expiry = datetime.datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    expiry_text = f"<t:{int(expiry.timestamp())}:R>"
                except:
                    expiry_text = expires_at
            
            task_config = config.get('task_config') or config.get('taskConfigV2') or config.get('taskConfig', {})
            tasks = task_config.get('tasks', {})
            publisher = messages.get('game_publisher') or config.get('game_publisher', 'Unknown')
            task_name = next(iter(tasks.keys()), 'Unknown')
            game_title = messages.get('game_title') or messages.get('gameTitle', 'Unknown Game')
            task_data = tasks.get(task_name, {})
            seconds_needed = task_data.get('target', 0)
            minutes = seconds_needed // 60
            
            assets = config.get('assets', {})
            image_url = None
            for key in ['quest_bar_hero', 'hero']:
                asset_path = assets.get(key)
                if asset_path:
                    if asset_path.startswith('quests/'):
                        image_url = f"https://cdn.discordapp.com/{asset_path}"
                    else:
                        image_url = f"https://cdn.discordapp.com/quests/{q_id}/{asset_path}"
                    break

            gallery = discord.ui.MediaGallery(discord.MediaGalleryItem(image_url,description="Quest Image"))
            v = ui.LayoutView(timeout=None)
            c = ui.Container(
                ui.TextDisplay("### New Quest Available!"),
                gallery,
                ui.Separator(),
                ui.TextDisplay(f"### Quest Info\n**Duration:** {minutes} - {expiry_text}\n**Game:** {quest_name}\n**Publisher:** {config.get('publisher', 'Unknown')}"),
                ui.Separator(),
                ui.TextDisplay(f"### Tasks\n{task_name.replace('_', ' ').title()}\n**ID:** `{q_id}`"),
                ui.Separator(),
                ui.TextDisplay(f"-# {game_title},Use !quest to start this quest"),
                ui.ActionRow(
                    ui.Button(label="View Quest", style=discord.ButtonStyle.link, url=f"https://discord.com/quests/{q_id}")
                )
            )
            v.add_item(c)
            
            try:
                await channel.send(view=v)
            except Exception as e:
                print(f"Error sending notification: {e}")
    
    @commands.command(name='questnotify')
    async def setup_notify(self, ctx):
        """Set up quest notifications in this channel"""
        conn = sqlite3.connect('store.db')
        row = conn.execute('SELECT token FROM token WHERE user_id = ?', (str(ctx.author.id),)).fetchone()
        
        if not row:
            conn.close()
            return await ctx.send("❌ Use `!link` first to connect your Discord account")
        
        conn.execute(
            'UPDATE token SET notify_channel = ? WHERE user_id = ?',
            (str(ctx.channel.id), str(ctx.author.id))
        )
        conn.commit()
        conn.close()
        
        await ctx.send(f"✅ Quest notifications enabled in {ctx.channel.mention}!\nYou'll be notified when new quests are available.")
    
    @commands.command(name='disablenotify')
    async def disable_notify(self, ctx):
        """Disable quest notifications"""
        conn = sqlite3.connect('store.db')
        conn.execute(
            'UPDATE token SET notify_channel = NULL WHERE user_id = ?',
            (str(ctx.author.id),)
        )
        conn.commit()
        conn.close()
        
        await ctx.send("✅ Quest notifications disabled")
    
    @commands.command(name='checkquests')
    @commands.is_owner()
    async def check_quests_manual(self, ctx):
        """Manually trigger quest check (owner only)"""
        await ctx.send("🔍 Checking for new quests...")
        await self.check_new_quests()
        await ctx.send("✅ Quest check complete!")


async def setup(bot):
    conn = sqlite3.connect('store.db')
    try:
        conn.execute('ALTER TABLE token ADD COLUMN notify_channel TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.close()
    
    await bot.add_cog(QuestNotifier(bot))
