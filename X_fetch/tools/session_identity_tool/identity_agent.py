import random
from typing import Dict, Optional, Any
from core.utils.common import setup_logging, get_random_user_agent

logger = setup_logging("SessionIdentityAgent")

class SessionIdentityAgent:
    def __init__(self):
        self.proxy_list = [] # Load from config
        self.sessions = {}

    def get_session_config(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "user_agent": get_random_user_agent(),
                "proxy": self._get_random_proxy(),
                "cookies": {},
                "fingerprint": self._generate_fingerprint()
            }
        return self.sessions[session_id]

    def _get_random_proxy(self) -> Optional[str]:
        if not self.proxy_list:
            return None
        return random.choice(self.proxy_list)

    def _generate_fingerprint(self) -> Dict[str, Any]:
        # Generate randomized browser fingerprint parameters
        return {
            "viewport": {"width": random.randint(1280, 1920), "height": random.randint(720, 1080)},
            "device_scale_factor": random.choice([1, 2]),
            "is_mobile": False,
            "has_touch": False
        }

    def rotate_proxy(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id]["proxy"] = self._get_random_proxy()
            logger.info(f"Rotated proxy for session: {session_id}")
