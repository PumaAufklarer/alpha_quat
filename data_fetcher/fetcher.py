"""Tushare data fetcher."""
import json
from pathlib import Path
from typing import Optional

import tushare as ts

from .tushare_api import TushareAPI


class TushareFetcher:
    """Tushare data fetcher class."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize TushareFetcher with token from config.

        Args:
            config_path: Path to config.json file. If None, looks in project root.
        """
        if config_path is None:
            # 默认在项目根目录查找config.json
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config.json"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        token = config.get("tushare", {}).get("token")
        if not token or token == "your_tushare_token_here":
            raise ValueError("Please set your tushare token in config.json")

        # 初始化tushare pro api
        self.pro = ts.pro_api(token)
        self.api = TushareAPI(self.pro)

    def get_pro_api(self):
        """Get the tushare pro api instance."""
        return self.pro

    def get_api_wrapper(self):
        """Get the tushare api wrapper with rate limit handling."""
        return self.api
