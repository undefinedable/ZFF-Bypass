import requests

def send_uid_log(webhook_url: str, uid: str):
    payload = {
        "content": "Someone just used BypassUID",
        "embeds": [
            {
                "title": "UID Bypass Monitor",
                "description": f"> **UID:** `{uid}`",
                "color": 0x4A90E2,
                "footer": {
                    "text": "ZLabs • UID Monitor"
                }
            }
        ]
    }

    r = requests.post(webhook_url, json=payload)
    return r.status_code, r.text
