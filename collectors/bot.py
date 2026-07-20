import asyncio
from dataclasses import dataclass
from datetime import datetime

from astrbot.api import logger
from ..config import config
from ..misc_statistics import bot_connect_time, bot_info_cache, recv_num, send_num
from ..util import format_timedelta
from . import normal_collector


@dataclass
class BotStatus:
    self_id: str
    adapter: str
    nick: str
    bot_connected: str
    msg_rec: str
    msg_sent: str


async def get_bot_status(bot_id: str, adapter_name: str, now_time: datetime) -> BotStatus:
    nick = "AstrBot"
    if bot_id in bot_info_cache:
        info = bot_info_cache[bot_id]
        nick = info.get("nick") or info.get("name") or info.get("id") or "AstrBot"

    bot_connected = (
        format_timedelta(now_time - t)
        if (t := bot_connect_time.get(bot_id))
        else "未知"
    )

    msg_rec = recv_num.get(bot_id, 0)
    msg_sent = send_num.get(bot_id, 0)
    msg_rec = str(msg_rec)
    msg_sent = str(msg_sent)

    return BotStatus(
        self_id=bot_id,
        adapter=adapter_name,
        nick=nick,
        bot_connected=bot_connected,
        msg_rec=msg_rec,
        msg_sent=msg_sent,
    )


@normal_collector()
async def bots() -> list[BotStatus]:
    from ..config import config
    now_time = datetime.now().astimezone()

    if bot_info_cache:
        if config.ps_show_current_bot_only:
            # 只返回第一个（当前 Bot）
            first_id = next(iter(bot_info_cache.keys()))
            return [await get_bot_status(first_id, "AstrBot", now_time)]
        return [
            await get_bot_status(bid, "AstrBot", now_time)
            for bid in bot_info_cache.keys()
        ]

    return [BotStatus(
        self_id="0",
        adapter="AstrBot",
        nick="AstrBot",
        bot_connected="未知",
        msg_rec="0",
        msg_sent="0",
    )]
