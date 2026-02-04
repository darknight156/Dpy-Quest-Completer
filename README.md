# 🎯 Discord Quest Automation Bot

> **Automate Discord Quests with Speed and Style**  
> A powerful, open-source Discord bot for automating quest completion with real-time progress tracking and intelligent task handling.

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.0+-5865F2?style=for-the-badge&logo=discord)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Open Source](https://img.shields.io/badge/Open%20Source-Yes-brightgreen?style=for-the-badge)](https://github.com)

---

## ✨ Features

- 🚀 **Fast Quest Completion** - Multiple speed modes (Normal/Fast) for automated quest solving
- 🎮 **Multi-Quest Support** - Handle video quests, play quests, and activity quests
- 📊 **Real-Time Progress** - Live progress tracking with visual indicators
- 🔔 **Smart Notifications** - Auto-detect and notify new quests as they appear
- 🎨 **Beautiful UI** - Interactive Discord embeds with intuitive controls
- ⚡ **Throttled Updates** - Optimized UI rendering for smooth performance
- 🔐 **Secure Token Management** - Local SQLite storage for user tokens
- 📱 **Cross-Platform** - Support for Android and iOS token extraction

---

## 🏗️ Project Structure

```
Quest-Bot/
├── main.py                 # Bot initialization and core setup
├── handler/
│   └── handler.py         # Quest execution logic (video, play, activity)
├── cogs/
│   ├── quest.py           # Quest UI and selection interface
│   ├── token.py           # Token management and linking
│   └── notifier.py        # Quest notification system
├── utils/
│   └── header.py          # API header utilities
└── store.db               # SQLite database for token storage
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- `discord.py` 2.0+
- `aiohttp` for async HTTP requests
- A Discord bot token

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/darknight156/Dpy-Quest-Completer.git
   cd Dpy-Quest-Completer
   ```

2. **Install dependencies**
   ```bash
   pip install discord.py aiohttp
   ```

3. **Set up your bot token**
   - Create a Discord application at [Discord Developer Portal](https://discord.com/developers/applications)
   - Copy your bot token and update `main.py`:
   ```python
   bot.run('YOUR_BOT_TOKEN_HERE')
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

---

## 📖 How It Works

### 1. **Token Linking**
```
!link → Token Modal → Android/iOS Scripts → Token Stored in SQLite
```
Users securely link their Discord account by providing their user token. The bot provides platform-specific bookmarklet scripts to extract tokens safely.

### 2. **Quest Discovery**
```
!quest → Fetch Active Quests → Display with Interactive UI
```
The bot fetches all available quests from Discord API and presents them in an interactive select menu, filtering out expired or completed quests.

### 3. **Quest Execution**
```
Select Quest → Choose Mode (Normal/Fast) → Auto-Complete → Notify User
```
Select your quest, choose your speed mode, and the bot handles the rest:
- **Video Quests**: Progressively "watch" videos by sending timestamp updates
- **Play Quests**: Simulate gameplay with periodic heartbeat requests
- **Activity Quests**: Participate in activities with real-time progress tracking

### 4. **Smart Notifications**
```
Background Loop → Detect New Quests → Notify User in DM/Channel
```
The notifier continuously monitors for new quests and alerts users, eliminating the need for manual checking.

---

## 🎮 Command Reference

### User Commands

| Command | Description |
|---------|-------------|
| `!link` | Link your Discord account to the bot |
| `!quest` | View and select available quests |
| `!stop` | Stop an active quest |

### UI Controls

**Quest Selection View**
- 🎯 **ORBS Quest Select** - Filter for quests with special rewards
- 📋 **Quest Select** - View all available quests

**Quest Control Panel**
- **Start** - Begin quest with current mode
- **Normal** - Set to normal completion speed
- **Fast** - Enable fast completion mode
- **Stop** - Halt the active quest
- **Enroll** - Enroll in quest if not already enrolled

---

## 🔧 Technical Details

### Speed Modes

**Normal Mode**
- Video: 15 sec increments, 0.5s interval
- Play: 60s heartbeat interval
- Activity: 20s interval

**Fast Mode** ⚡
- Video: 60 sec increments, 0.15s interval (4x faster)
- Play: 30s heartbeat interval
- Activity: 10s interval
- UI throttling every 2 updates (reduces overhead)

## 🔐 Security Considerations

⚠️ **Important**: This bot requires user tokens for operation. Be aware that:
- Store tokens securely (never commit to version control)
- Use environment variables for sensitive data
- Tokens should be treated like passwords
- Consider implementing token encryption for production use

### Best Practices
```python
# Use environment variables
import os
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
bot.run(TOKEN)
```

---

## 🎨 UI Features

### Interactive Embeds
- Quest details with images
- Real-time progress bars
- Reward information
- Expiration timestamps
- Enrollment status indicators

---

## 📊 Performance Optimizations

1. **UI Throttling** - Progress updates only every N server requests
2. **Async Operations** - Full async/await for non-blocking I/O
3. **Connection Pooling** - Reusable aiohttp sessions
4. **Task Management** - Efficient task tracking with minimal overhead
5. **Background Tasks** - Non-blocking quest monitoring

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🌟 Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Inspired by the Discord community
- Thanks to all contributors and users

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/darknight156/Dpy-Quest-Completer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/darknight156/Dpy-Quest-Completer/discussions)
- **Discord**: [Join Our Server](https://discord.gg/https://discord.gg/f3kJUY4RdV)

---

<div align="center">

**Made with ❤️ for the Discord community**

⭐ If you find this project useful, please give it a star!

</div>
