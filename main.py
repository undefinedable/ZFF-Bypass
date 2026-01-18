import os, threading, time, sys, requests, glob

# ---------------------------------------------------------------------------
# Detect and configure Python environment inside Pterodactyl container.
#
# This ensures that user-installed site-packages under
# /home/container/.local/lib/pythonX.Y/site-packages are included in sys.path,
# allowing the application to access dependencies installed via Pterodactyl Python Eggs.
#
# Reference:
# https://github.com/HaseoTM/parkervcp-eggs/blob/master/generic/python/egg-python-generic.json
# ---------------------------------------------------------------------------
if os.path.exists("/home/container") and os.getenv("PTERODACTYL_SERVER_UUID"):
    paths = glob.glob("/home/container/.local/lib/python*/site-packages")
    for p in paths:
        if p not in sys.path:
            sys.path.append(p)

from libs.bot import UIDBot
from libs.api import ZeppelinAPI
from libs.services import UIDService
from libs.webhook import send_uid_log
from config.config import load_config

from mitmproxy import http
from mitmproxy.tools.main import mitmdump

services = UIDService()
config = load_config()

class MajorLoginInterceptor:
    def __init__(self, api_client: ZeppelinAPI, target: str = "/MajorLogin"):
        self.api = api_client
        self.target = target

    def _match(self, flow: http.HTTPFlow) -> bool:
        return flow.request.method == "POST" and self.target in flow.request.path

    # ---------------------------------- REQUEST --------------------------------- #
    def request(self, flow: http.HTTPFlow):
        if not self._match(flow):
            return

        result = self.api.post("modify_protobuf", flow.request.content.hex())
        if not result.get("success"):
            return

        try:
            flow.request.content = bytes.fromhex(result["data"])
            print("[MODIFY] OK - request body updated")
        except Exception as e:
            print(f"[MODIFY] ERROR convert hex -> bytes: {e}")

    # ---------------------------------- RESPONSE --------------------------------- #
    def response(self, flow: http.HTTPFlow):
        if not self._match(flow):
            return

        result = self.api.post("get_uid", flow.response.content.hex())
        if result.get("success"):
            uid = str(result['data'])
            status = services.uid_exists(uid)
            if not status:
                flow.response.content = (
                    f"[1E90FF]┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    f"[FFFF00][B] UID [FF0000]{uid} [FFFF00][B] NOT FOUND IN OUR DATABASE\n"
                    f"[1E90FF]┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    f"[FFFF00]t.me/zeppelinlabs\n"
                ).encode()
                flow.response.status_code = 400
                return
            if config.get("use_webhook", False):
                send_uid_log(config["discord"]["webhook_url"], uid)
        else:
            flow.response.content = (
                "t.me/zeppelinlabs"
            ).encode()
            flow.response.status_code = 400


class ZLabs:
    @staticmethod
    def run_proxy(port: int):
        ip = requests.get("https://ipinfo.io/ip", timeout=5).text.strip()
        
        print("=====" * 10)
        print(f"🟢  Status   : ONLINE")
        print(f"🌐  IP       : {ip}")
        print(f"🔌  Port     : {port}")
        print(f"➡️  Connect to proxy server {ip}:{port}")
        print("=====" * 10)
        
        confdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")
        mitmdump([
            "-s", os.path.basename(__file__),
            "-p", str(port),
            "--set", "block_global=false",
            "--set", f"confdir={confdir}"
        ])
    
    @staticmethod
    def run_bot(token: str):
        """ Run Discord bot only. """
        bot = UIDBot(token=token)
        bot.run()


api = ZeppelinAPI(config["api_url"])
addons = [MajorLoginInterceptor(api)]

if __name__ == "__main__":
    if config.get("use_bot", False):
        discord_cfg = config.get("discord", {})
        threading.Thread(
            target=ZLabs.run_bot,
            args=(discord_cfg["bot_token"], ),
            daemon=True
        ).start()
    ZLabs.run_proxy(port=config["proxy_port"])
