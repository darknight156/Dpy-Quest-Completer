# Made By DarkNighT (- mmiiiuu)
# Made By DarkNighT (- mmiiiuu)
# Made By DarkNighT (- mmiiiuu)

import discord
import sqlite3
import asyncio
import datetime
import json
import aiohttp

from discord.ext import commands
from discord import ui

from utils.header import get_headers
from handler.handler import (
    handle_video_quest,
    handle_play_quest,
    solve_quest,
    stop_quest_task,
)

class OrbsQuestSelect(discord.ui.Select):
    def __init__(self, quests, token):
        options = []
        self.q_map = {}

        for q in quests[:25]:
            q_id = q["id"]
            config = q.get("config", {})
            messages = config.get("messages", {})

            name = (
                messages.get("quest_name")
                or messages.get("questName")
                or "Unknown Quest"
            )

            rewards_config = config.get("rewards_config", {})
            rewards = rewards_config.get("rewards", [])
            
            has_orbs = False
            if rewards:
                for reward in rewards:
                    orb_quantity = reward.get("orb_quantity")
                    if orb_quantity and orb_quantity > 0:
                        has_orbs = True
                        break

            if not has_orbs:
                continue

            task_config = (
                config.get("task_config")
                or config.get("taskConfigV2")
                or config.get("taskConfig", {})
            )

            tasks = list(task_config.get("tasks", {}).keys())

            self.q_map[q_id] = {
                "name": name,
                "config": config,
                "full_quest": q,
            }

            task_desc = (
                f"Tasks: {', '.join(tasks)[:100]}"
                if tasks
                else "No tasks"
            )

            options.append(
                discord.SelectOption(
                    label=name[:100],
                    value=q_id,
                    emoji="<:orbs:1468288598980821195>"
                )
            )

        super().__init__(
            placeholder="Select an ORBS quest to solve...",
            options=options or [
                discord.SelectOption(
                    label="No Orbs quests found",
                    value="none",
                    default=True,
                )
            ],
            row=1,
            disabled=not options,
        )

        self.token = token

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            await interaction.response.send_message(
                "❌ No Orbs quests available",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        q_data = self.q_map[self.values[0]]

        view = QuestControlView(
            self.token,
            self.values[0],
            q_data["name"],
            q_data["config"],
            q_data["full_quest"],
        )

        await interaction.followup.send(view=view, ephemeral=False)
        
class QuestSelect(discord.ui.Select):
    def __init__(self, quests, token):
        options = []
        self.q_map = {}

        for q in quests[:25]:
            q_id = q["id"]
            config = q.get("config", {})
            messages = config.get("messages", {})

            name = (
                messages.get("quest_name")
                or messages.get("questName")
                or "Unknown Quest"
            )

            task_config = (
                config.get("task_config")
                or config.get("taskConfigV2")
                or config.get("taskConfig", {})
            )

            tasks = list(task_config.get("tasks", {}).keys())

            self.q_map[q_id] = {
                "name": name,
                "config": config,
                "full_quest": q,
            }

            task_desc = (
                f"Tasks: {', '.join(tasks)[:100]}"
                if tasks
                else "No tasks"
            )

            options.append(
                discord.SelectOption(
                    label=name[:100],
                    value=q_id,
                )
            )

        super().__init__(
            placeholder="Select a quest to solve...",
            options=options,
            row=0,
        )

        self.token = token

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        q_data = self.q_map[self.values[0]]

        view = QuestControlView(
            self.token,
            self.values[0],
            q_data["name"],
            q_data["config"],
            q_data["full_quest"],
        )

        await interaction.followup.send(view=view, ephemeral=False)

class QuestControlView(discord.ui.LayoutView):
    def __init__(self, token, q_id, q_name, quest_config, full_quest):
        super().__init__(timeout=300)

        self.token = token
        self.q_id = q_id
        self.q_name = q_name
        self.quest_config = quest_config
        self.full_quest = full_quest

        self.speed_mode = "normal"
        self.is_running = False
        self.quest_task = None

        container = self.create_quest_embed()
        self.add_item(container)

    def get_quest_image(self):
        assets = self.quest_config.get("assets", {})
        q_id = self.q_id
        
        priority_keys = [
            "quest_bar_hero", 
            "hero", 
        ]
        
        for key in priority_keys:
            asset_path = assets.get(key)
            if asset_path:
                if asset_path.startswith("quests/"):
                    return f"https://cdn.discordapp.com/{asset_path}"
                else:
                    return f"https://cdn.discordapp.com/quests/{q_id}/{asset_path}"
        
        return None
    
    def get_reward_name(self):
        """Get reward name from rewards_config based on TypeScript interface"""
        rewards_config = self.quest_config.get("rewards_config", {})
        rewards = rewards_config.get("rewards", [])
        
        if rewards:
            reward_messages = rewards[0].get("messages", {})
            reward_name = reward_messages.get("name")
            if reward_name:
                return reward_name
            
            reward_name_with_article = reward_messages.get("name_with_article")
            if reward_name_with_article:
                return reward_name_with_article
        
        old_rewards = self.quest_config.get("rewards", [])
        if old_rewards:
            return old_rewards[0].get("reward_code", "Unknown Reward")
        
        return "Unknown Reward"
    
    def is_enrolled(self):
        """Check if user is enrolled in quest"""
        user_status = self.full_quest.get("user_status")
        if not user_status:
            return False
        return user_status.get("enrolled_at") is not None
    
    def create_quest_embed(self):
        config = self.quest_config

        task_config = (
            config.get("task_config")
            or config.get("taskConfigV2")
            or config.get("taskConfig")
            or {}
        )

        tasks = task_config.get("tasks", {})
        task_name = next(iter(tasks.keys()), "Unknown")
        task_data = tasks.get(task_name, {})

        seconds_needed = task_data.get("target", 0)
        minutes = seconds_needed // 60

        reward_name = self.get_reward_name()

        user_status = self.full_quest.get("user_status") or {}
        progress_data = user_status.get("progress", {})
        current_progress = progress_data.get(task_name, {}).get("value", 0)

        progress_percent = (
            int((current_progress / seconds_needed) * 100)
            if seconds_needed > 0
            else 0
        )

        expires_at = config.get("expires_at") or config.get("expiresAt")
        expiry_text = "Unknown"

        if expires_at:
            try:
                expiry = datetime.datetime.fromisoformat(
                    expires_at.replace("Z", "+00:00")
                )
                expiry_text = f"<t:{int(expiry.timestamp())}:R>"
            except Exception:
                expiry_text = expires_at

        image_url = self.get_quest_image()
        is_enrolled = self.is_enrolled()
        enrollment_status = "✅ Enrolled" if is_enrolled else "❌ Not Enrolled"

        items = [
            ui.TextDisplay(f"### {self.q_name}"),
            ui.Separator(),
            ui.TextDisplay(
                f"**Reward:** {reward_name}\n"
                f"**Type:** {task_name.replace('_', ' ').title()}\n"
                f"**Time:** {minutes} minutes\n"
                f"**Progress:** {progress_percent}%\n"
                f"**Expires:** {expiry_text}"
            ),
        ]

        if image_url:
            items.extend(
                [
                    ui.Separator(),
                    discord.ui.MediaGallery(
                        discord.MediaGalleryItem(
                            image_url,
                            description="Quest Image",
                        )
                    ),
                ]
            )

        items.extend(
            [
                ui.Separator(),
                ui.TextDisplay(f"Quest id: `{self.q_id}`"),
                ui.Separator(),
                discord.ui.ActionRow(
                    discord.ui.Button(
                        label="Start",
                        style=discord.ButtonStyle.secondary,
                        custom_id="quest_start",
                    ),
                    discord.ui.Button(
                        label="Normal",
                        style=discord.ButtonStyle.secondary,
                        custom_id="quest_normal",
                    ),
                    discord.ui.Button(
                        label="Fast",
                        style=discord.ButtonStyle.secondary,
                        custom_id="quest_fast",
                    ),
                    discord.ui.Button(
                        label="Stop",
                        style=discord.ButtonStyle.secondary,
                        custom_id="quest_stop",
                    ),
                    discord.ui.Button(
                        label="Enroll",
                        style=discord.ButtonStyle.primary,
                        custom_id="quest_enroll",
                        disabled=is_enrolled,
                    ),
                ),
            ]
        )

        return discord.ui.Container(*items)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.data.get("custom_id"):
            return True

        custom_id = interaction.data["custom_id"]

        if custom_id == "quest_start":
            await self._handle_start(interaction)
        elif custom_id == "quest_normal":
            await self._handle_normal(interaction)
        elif custom_id == "quest_fast":
            await self._handle_fast(interaction)
        elif custom_id == "quest_stop":
            await self._handle_stop(interaction)
        elif custom_id == "quest_enroll":
            await self._handle_enroll(interaction)
        return False

    async def _handle_start(self, interaction: discord.Interaction):
        if self.is_running:
            await interaction.response.send_message(
                "❌ Quest already running!",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        self.is_running = True
        self.quest_task = asyncio.create_task(
            solve_quest(
                interaction,
                self.token,
                self.q_id,
                self.q_name,
                self.quest_config,
                self,
            )
        )

        await interaction.followup.send(
            f"✅ Quest started in **{self.speed_mode}** mode! Check your DMs.",
            ephemeral=True,
        )

    async def _handle_normal(self, interaction: discord.Interaction):
        if self.is_running:
            if self.quest_task:
                self.quest_task.cancel()

            self.speed_mode = "normal"

            await interaction.response.defer(ephemeral=True)
            await asyncio.sleep(0.5)

            self.is_running = True
            self.quest_task = asyncio.create_task(
                solve_quest(
                    interaction,
                    self.token,
                    self.q_id,
                    self.q_name,
                    self.quest_config,
                    self.speed_mode,
                )
            )

            await interaction.followup.send(
                "🔄 Quest restarted in **normal** mode!",
                ephemeral=True,
            )
        else:
            self.speed_mode = "normal"
            await interaction.response.send_message(
                "✅ Mode set to **normal**",
                ephemeral=True,
            )

    async def _handle_fast(self, interaction: discord.Interaction):
        if self.is_running:
            if self.quest_task:
                self.quest_task.cancel()

            self.speed_mode = "fast"

            await interaction.response.defer(ephemeral=True)
            await asyncio.sleep(0.5)

            self.is_running = True
            self.quest_task = asyncio.create_task(
                solve_quest(
                    interaction,
                    self.token,
                    self.q_id,
                    self.q_name,
                    self.quest_config,
                    self.speed_mode,
                )
            )

            await interaction.followup.send(
                "🔄 Quest restarted in **fast** mode!",
                ephemeral=True,
            )
        else:
            self.speed_mode = "fast"
            await interaction.response.send_message(
                "✅ Mode set to **fast**",
                ephemeral=True,
            )

    async def _handle_stop(self, interaction: discord.Interaction):
        if not self.is_running or not self.quest_task:
            await interaction.response.send_message(
                "❌ No quest is running!",
                ephemeral=True,
            )
            return

        self.quest_task.cancel()
        self.is_running = False

        await interaction.response.send_message(
            "⏹️ Quest stopped!",
            ephemeral=True,
        )

        try:
            await interaction.response.send_message(
                "⏹️ Quest has been stopped by user.",
                ephemeral=True,
            )
        except Exception:
            pass
        
    async def _handle_enroll(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        headers = get_headers(self.token)
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"https://discord.com/api/v9/quests/{self.q_id}/enroll",
                    headers=headers,
                    json={
                        "location": 11, 
                    }
                ) as resp:
                    if resp.status in (200, 204):
                        response_data = await resp.json() if resp.status == 200 else {}
                        if response_data:
                            self.full_quest["user_status"] = response_data
                        
                        await interaction.followup.send(
                            f"✅ Successfully enrolled in **{self.q_name}**!",
                            ephemeral=True
                        )
                        
                        self.clear_items()
                        container = self.create_quest_embed()
                        self.add_item(container)
                        
                    else:
                        error_text = await resp.text()
                        await interaction.followup.send(
                            f"❌ Failed to enroll: {error_text[:200]}",
                            ephemeral=True
                        )
            except Exception as e:
                await interaction.followup.send(
                    f"❌ Error enrolling: {str(e)}",
                    ephemeral=True
                )


class QuestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @commands.command(name='quest')
    async def quest(self, ctx):
        conn = sqlite3.connect('store.db')
        row = conn.execute('SELECT token FROM token WHERE user_id = ?', (str(ctx.author.id),)).fetchone()
        conn.close()
        if not row:
            return await ctx.send("Use `!link` first")
        
        token = row[0]
        headers = get_headers(token)
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://discord.com/api/v9/quests/@me", headers=headers) as resp:
                    resp_text = await resp.text()
                    
                    if resp.status == 200:
                        data = json.loads(resp_text)
                        all_quests = data.get('quests', [])
                        found_quests = []
                        
                        for q in all_quests:
                            q_id = q.get('id')
                            if q_id == '1412491570820812933':
                                continue
                            
                            config = q.get('config', {})
                            user_status = q.get('user_status')
                            expires_at = config.get('expires_at') or config.get('expiresAt')
                            
                            if expires_at:
                                try:
                                    expiry = datetime.datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                                    if datetime.datetime.now(expiry.tzinfo) > expiry:
                                        continue
                                except:
                                    pass
                                
                            if user_status:
                                completed = user_status.get('completed_at') or user_status.get('completedAt')
                                if completed:
                                    continue
                                
                            found_quests.append(q)
                            
                        if not found_quests:
                            return await ctx.send(f"No quests found ({len(all_quests)} total)")
                        
                        view = discord.ui.View()
                        view.add_item(OrbsQuestSelect(found_quests, token))
                        view.add_item(QuestSelect(found_quests, token))
                        await ctx.send(f"🎯 Found {len(found_quests)} quest(s):", view=view)
                        
                    elif resp.status == 401:
                        await ctx.send("Invalid token. Use `!link`")
                    elif resp.status == 403:
                        await ctx.send("Access forbidden")
                    else:
                        await ctx.send(f"❌ API Error {resp.status}: {resp_text[:200]}")
            except Exception as e:
                await ctx.send(f"Error: {str(e)}")
                
                
async def setup(bot):
    await bot.add_cog(QuestCog(bot))
    
