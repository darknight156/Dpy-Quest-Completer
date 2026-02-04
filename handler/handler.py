import asyncio
import aiohttp
import random
import discord
from utils.header import get_headers

running_tasks = {}

def stop_quest_task(user_id, q_id):
    key = f"{user_id}_{q_id}"
    task = running_tasks.pop(key, None)
    if task:
        task.cancel()
        return True
    return False


def build_view(title, lines):
    view = discord.ui.LayoutView()
    c = discord.ui.Container(
        discord.ui.TextDisplay(f"### {title}"),
        discord.ui.Separator(),
        discord.ui.TextDisplay(f"```ruby\n" + "\n".join(lines[-10:]) + "\n```"),
    )
    view.add_item(c)
    return view


async def handle_video_quest(
    message,
    session,
    headers,
    q_id,
    q_name,
    seconds_needed,
    quest_view=None,
    speed_mode="normal",
):
    if quest_view:
        speed_mode = quest_view.speed_mode

    if speed_mode == "fast":
        max_future, speed, interval = (60, 60, 0.15)
        ui_throttle = 2
    else:
        max_future, speed, interval = (30, 30, 0.4)
        ui_throttle = 1

    enrolled_at = asyncio.get_event_loop().time()
    seconds_done = 0
    progress_lines = []
    completed = False
    ui_counter = 0

    await message.edit(view=build_view(q_name, ["Starting quest..."]))

    try:
        while not completed and seconds_done < seconds_needed:
            max_allowed = int((asyncio.get_event_loop().time() - enrolled_at)) + max_future
            diff = max_allowed - seconds_done

            if diff >= speed:
                timestamp = min(seconds_needed, seconds_done + speed + random.random())
                payload = {"timestamp": timestamp}

                async with session.post(
                    f"https://discord.com/api/v9/quests/{q_id}/video-progress",
                    headers=headers,
                    json=payload,
                ) as resp:
                    if resp.status != 200:
                        return

                    data = await resp.json()
                    completed = data.get("completed_at") is not None
                    seconds_done = int(timestamp)

                    percent = int((seconds_done / seconds_needed) * 100)
                    ui_counter += 1
                    if ui_counter >= ui_throttle or completed:
                        progress_lines.append(f"[PROGRESS] {percent}%")
                        await message.edit(
                            view=build_view(
                                "Quest Completed!" if completed else q_name,
                                progress_lines,
                            )
                        )
                        ui_counter = 0

            await asyncio.sleep(interval)

        await session.post(
            f"https://discord.com/api/v9/quests/{q_id}/video-progress",
            headers=headers,
            json={"timestamp": seconds_needed},
        )

        if not progress_lines or progress_lines[-1] != "[PROGRESS] 100%":
            progress_lines.append("[PROGRESS] 100%")

        await message.edit(view=build_view("Quest Completed!", progress_lines))

    except asyncio.CancelledError:
        await message.edit(view=build_view("Quest Stopped", ["Quest was stopped by user."]))
        raise


async def handle_play_quest(
    message,
    session,
    headers,
    q_id,
    q_name,
    seconds_needed,
    quest_config,
    quest_view=None,
    speed_mode="normal",
):
    if quest_view:
        speed_mode = quest_view.speed_mode

    app_id = quest_config.get("application", {}).get("id")
    if not app_id:
        await message.edit(view=build_view(q_name, ["❌ Application ID missing"]))
        return

    interval = 30 if speed_mode == "fast" else 60
    seconds_done = 0
    progress_lines = []
    ui_counter = 0
    ui_throttle = 2 if speed_mode == "fast" else 1

    await message.edit(view=build_view(q_name, ["Starting quest..."]))

    try:
        while seconds_done < seconds_needed:
            payload = {"application_id": app_id, "terminal": False}

            async with session.post(
                f"https://discord.com/api/v9/quests/{q_id}/heartbeat",
                headers=headers,
                json=payload,
            ) as resp:
                if resp.status != 200:
                    return

                data = await resp.json()
                progress = data.get("progress", {}).get("PLAY_ON_DESKTOP", {})
                seconds_done = progress.get("value", 0)

                percent = int((seconds_done / seconds_needed) * 100)
                ui_counter += 1
                if ui_counter >= ui_throttle or seconds_done >= seconds_needed:
                    progress_lines.append(f"[PROGRESS] {percent}%")
                    await message.edit(view=build_view(q_name, progress_lines))
                    ui_counter = 0

            await asyncio.sleep(interval)

        await session.post(
            f"https://discord.com/api/v9/quests/{q_id}/heartbeat",
            headers=headers,
            json={"application_id": app_id, "terminal": True},
        )

        if not progress_lines or progress_lines[-1] != "[PROGRESS] 100%":
            progress_lines.append("[PROGRESS] 100%")

        await message.edit(view=build_view("Quest Completed!", progress_lines))

    except asyncio.CancelledError:
        await session.post(
            f"https://discord.com/api/v9/quests/{q_id}/heartbeat",
            headers=headers,
            json={"application_id": app_id, "terminal": True},
        )
        await message.edit(view=build_view("Quest Stopped", ["Quest was stopped by user."]))
        raise


async def handle_activity_quest(
    message,
    session,
    headers,
    q_id,
    q_name,
    seconds_needed,
    quest_view=None,
    speed_mode="normal",
):
    if quest_view:
        speed_mode = quest_view.speed_mode

    stream_key = "call:1:1"
    interval = 10 if speed_mode == "fast" else 20
    seconds_done = 0
    progress_lines = []
    ui_counter = 0
    ui_throttle = 2 if speed_mode == "fast" else 1

    await message.edit(view=build_view(q_name, ["Starting quest..."]))

    try:
        while seconds_done < seconds_needed:
            payload = {"stream_key": stream_key, "terminal": False}

            async with session.post(
                f"https://discord.com/api/v9/quests/{q_id}/heartbeat",
                headers=headers,
                json=payload,
            ) as resp:
                if resp.status != 200:
                    return

                data = await resp.json()
                progress = data.get("progress", {}).get("PLAY_ACTIVITY", {})
                seconds_done = progress.get("value", 0)

                percent = int((seconds_done / seconds_needed) * 100)
                ui_counter += 1
                if ui_counter >= ui_throttle or seconds_done >= seconds_needed:
                    progress_lines.append(f"[PROGRESS] {percent}%")
                    await message.edit(view=build_view(q_name, progress_lines))
                    ui_counter = 0

            await asyncio.sleep(interval)

        await session.post(
            f"https://discord.com/api/v9/quests/{q_id}/heartbeat",
            headers=headers,
            json={"stream_key": stream_key, "terminal": True},
        )

        if not progress_lines or progress_lines[-1] != "[PROGRESS] 100%":
            progress_lines.append("[PROGRESS] 100%")

        await message.edit(view=build_view("Quest Completed!", progress_lines))

    except asyncio.CancelledError:
        await session.post(
            f"https://discord.com/api/v9/quests/{q_id}/heartbeat",
            headers=headers,
            json={"stream_key": stream_key, "terminal": True},
        )
        await message.edit(view=build_view("Quest Stopped", ["Quest was stopped by user."]))
        raise


async def solve_quest(
    interaction,
    token,
    q_id,
    q_name,
    quest_config,
    quest_view=None,
    speed_mode="normal",
):
    headers = get_headers(token)

    try:
        dm_channel = await interaction.user.create_dm()
        dm_message = await dm_channel.send(
            view=build_view(q_name, ["Enrolling..."])
        )
    except:
        await interaction.followup.send("❌ Could not send DM. Please enable DMs from server members.", ephemeral=True)
        return

    async with aiohttp.ClientSession() as session:
        task_config = (
            quest_config.get("task_config")
            or quest_config.get("taskConfigV2")
            or quest_config.get("taskConfig", {})
        )

        tasks = task_config.get("tasks", {})
        task_name = next(
            (
                t
                for t in [
                    "WATCH_VIDEO",
                    "WATCH_VIDEO_ON_MOBILE",
                    "PLAY_ON_DESKTOP",
                    "PLAY_ACTIVITY",
                ]
                if t in tasks
            ),
            None,
        )

        if not task_name:
            await dm_message.edit(view=build_view(q_name, ["❌ Unknown quest type"]))
            return

        seconds_needed = tasks[task_name]["target"]

        enroll = await session.post(
            f"https://discord.com/api/v9/quests/{q_id}/enroll",
            headers=headers,
            json={"location": 11},
        )

        if enroll.status not in (200, 204):
            await dm_message.edit(view=build_view(q_name, ["❌ Enroll failed"]))
            return

        key = f"{interaction.user.id}_{q_id}"
        task = None

        if task_name.startswith("WATCH"):
            task = asyncio.create_task(
                handle_video_quest(
                    dm_message,
                    session,
                    headers,
                    q_id,
                    q_name,
                    seconds_needed,
                    quest_view,
                    speed_mode,
                )
            )
        elif task_name == "PLAY_ON_DESKTOP":
            task = asyncio.create_task(
                handle_play_quest(
                    dm_message,
                    session,
                    headers,
                    q_id,
                    q_name,
                    seconds_needed,
                    quest_config,
                    quest_view,
                    speed_mode,
                )
            )
        elif task_name == "PLAY_ACTIVITY":
            task = asyncio.create_task(
                handle_activity_quest(
                    dm_message,
                    session,
                    headers,
                    q_id,
                    q_name,
                    seconds_needed,
                    quest_view,
                    speed_mode,
                )
            )

        if task:
            running_tasks[key] = task
            await task
            running_tasks.pop(key, None)