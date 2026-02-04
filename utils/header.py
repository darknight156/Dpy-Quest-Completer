# Made By DarkNighT (- mmiiiuu)
# Made By DarkNighT (- mmiiiuu)
# Made By DarkNighT (- mmiiiuu)

import base64
from uuid import uuid4
import json

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9215 Chrome/138.0.7204.251 Electron/37.6.0 Safari/537.36'
CLIENT_BUILD_NUMBER = 471091

def get_super_properties():
    return {
        "os": "Windows",
        "browser": "Discord Client",
        "release_channel": "stable",
        "client_version": "1.0.9215",
        "os_version": "10.0.19045",
        "os_arch": "x64",
        "app_arch": "x64",
        "system_locale": "en-US",
        "has_client_mods": False,
        "client_launch_id": str(uuid4()),
        "browser_user_agent": USER_AGENT,
        "browser_version": "37.6.0",
        "os_sdk_version": "19045",
        "client_build_number": CLIENT_BUILD_NUMBER,
        "native_build_number": 72186,
        "client_event_source": None,
        "launch_signature": str(uuid4()),
        "client_heartbeat_session_id": str(uuid4()),
        "client_app_state": "focused"
    }

def get_headers(token):
    super_props = base64.b64encode(json.dumps(get_super_properties()).encode()).decode()
    return {
        'Authorization': token,
        'Accept': '*/*',
        'Accept-Language': 'en-US',
        'Content-Type': 'application/json',
        'User-Agent': USER_AGENT,
        'X-Super-Properties': super_props,
        'X-Discord-Locale': 'en-US',
        'X-Discord-Timezone': 'Asia/Saigon',
        'X-Debug-Options': 'bugReporterEnabled',
        'Origin': 'https://discord.com',
        'Referer': 'https://discord.com/channels/@me',
        'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Pragma': 'no-cache',
        'Priority': 'u=1, i'
    }
