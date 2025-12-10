import requests

class ZeppelinAPI:
    """ Zeppelin API Wrapper for Bypass Emulator Detection on Free Fire. """

    def __init__(self, url: str, timeout: int = 5):
        self.url = url.rstrip("/")
        self.timeout = timeout

    def post(self, operation: str, data: str) -> dict:
        payload = {
            "operation": operation,
            "data": data,
        }
        try:
            response = requests.post(self.url, json=payload, timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {"success": False, "message": str(e)}