"""统计信息模块"""
from datetime import datetime
from typing import Dict, Optional
import psutil
from astrbot.api import logger
import httpx

_process = psutil.Process()
_process_create_time = datetime.fromtimestamp(_process.create_time()).astimezone()

bot_connect_time: Dict[str, datetime] = {}
bot_info_cache: Dict[str, dict] = {}
bot_avatar_cache: Dict[str, bytes] = {}
recv_num: Dict[str, int] = {}
send_num: Dict[str, int] = {}
nonebot_run_time: Optional[datetime] = _process_create_time
bot_info_fetched: bool = False


def init_statistics():
    global nonebot_run_time
    if nonebot_run_time is None:
        nonebot_run_time = _process_create_time
    logger.debug("Statistics initialized")


async def cache_bot_avatar(avatar_url: str, bot_id: str, timeout: int = 10):
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(avatar_url)
            if resp.status_code == 200:
                bot_avatar_cache[bot_id] = resp.content
                logger.debug(f"Cached avatar for {bot_id}")
    except Exception:
        logger.debug(f"Failed to cache avatar for {bot_id}")


async def fetch_qq_avatar(qq_id: str, timeout: int = 10) -> bytes | None:
    url = f"https://q1.qlogo.cn/g?b=qq&nk={qq_id}&s=640"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.content
    except Exception as e:
        logger.debug(f"Failed to fetch QQ avatar: {e}")
    return None
