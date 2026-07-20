"""
AstrBot Plugin: PicStatus
移植自 nonebot-plugin-picstatus，以精美的卡片图片形式展示系统状态。
"""

import asyncio
from datetime import datetime

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import At, Image

from . import config as config_module
from .config import ConfigModel
from .bg_provider import bg_preloader
from .collectors import enable_collectors, load_builtin_collectors, registered_collectors, collect_all
from .templates import load_builtin_templates, loaded_templates, render_current_template
from .misc_statistics import (
    bot_connect_time, bot_info_cache, init_statistics,
    recv_num, send_num, bot_avatar_cache, bot_info_fetched,
    fetch_qq_avatar, _process_create_time
)


@register("astrbot_plugin_picstatus", "yuexps", "系统状态图片展示", "2.3.2-astrbot")
class PicStatusPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.context = context

        config_module.config = ConfigModel()
        global_config = config_module.config

        init_statistics()

        main_cfg = context.get_config()
        nicknames = main_cfg.get("nickname", ["AstrBot"])
        if isinstance(nicknames, str):
            self.fallback_nick = nicknames
        elif isinstance(nicknames, list) and nicknames:
            self.fallback_nick = nicknames[0]
        else:
            self.fallback_nick = "AstrBot"

        if global_config.ps_use_env_nick and nicknames:
            if isinstance(nicknames, str):
                self.fallback_nick = nicknames
            elif isinstance(nicknames, list) and nicknames:
                self.fallback_nick = nicknames[0]

        self._bot_id = self._resolve_bot_id()

        if self._bot_id not in bot_connect_time:
            bot_connect_time[self._bot_id] = _process_create_time
        if self._bot_id not in recv_num:
            recv_num[self._bot_id] = 0
        if self._bot_id not in send_num:
            send_num[self._bot_id] = 0
        if self._bot_id not in bot_info_cache:
            bot_info_cache[self._bot_id] = {
                "self_id": self._bot_id,
                "nick": self.fallback_nick,
                "name": self.fallback_nick,
                "id": self._bot_id,
            }

        if global_config.ps_template not in loaded_templates:
            load_builtin_templates()
        current_template = loaded_templates.get(global_config.ps_template)
        if current_template is None:
            raise ValueError(f"Template {global_config.ps_template} not found")

        if (current_template.collectors is None) or any(
            (x not in registered_collectors) for x in current_template.collectors
        ):
            load_builtin_collectors()

        collectors = (
            set(registered_collectors)
            if current_template.collectors is None
            else current_template.collectors
        )

        asyncio.create_task(self._startup(collectors))
        logger.info(f"PicStatus initialized (bot_id={self._bot_id})")

    def _resolve_bot_id(self) -> str:
        try:
            if hasattr(self.context, "platform") and self.context.platform:
                sid = getattr(self.context.platform, "self_id", None)
                if sid:
                    return str(sid)
            if hasattr(self.context, "platform_manager"):
                pm = self.context.platform_manager
                if hasattr(pm, "get_insts"):
                    platforms = pm.get_insts()
                    for p in platforms:
                        sid = getattr(p, "self_id", None)
                        if sid:
                            return str(sid)
        except Exception as e:
            logger.debug(f"Failed to resolve bot_id from context: {e}")
        return "default"

    async def _startup(self, collectors):
        await enable_collectors(*collectors)
        bg_preloader.start_preload()
        logger.info("PicStatus collectors started")

    async def _fetch_bot_info(self, event: AstrMessageEvent):
        global bot_info_fetched
        if bot_info_fetched:
            return

        platform_name = event.get_platform_name() if hasattr(event, "get_platform_name") else ""
        nick = bot_info_cache[self._bot_id].get("nick", self.fallback_nick)
        avatar_bytes = None
        real_connect_time = None

        try:
            if platform_name == "aiocqhttp" and hasattr(event, "bot") and event.bot:
                client = event.bot
                if hasattr(client, "api"):
                    try:
                        info = await client.api.call_action("get_login_info")
                        if info and isinstance(info, dict):
                            nick = info.get("nickname", nick)
                            qq_id = str(info.get("user_id", self._bot_id))
                            if qq_id and qq_id != "0" and qq_id != self._bot_id:
                                old_id = self._bot_id
                                self._bot_id = qq_id
                                bot_info_cache[qq_id] = bot_info_cache.pop(old_id, {})
                                bot_connect_time[qq_id] = bot_connect_time.pop(old_id, _process_create_time)
                                recv_num[qq_id] = recv_num.pop(old_id, 0)
                                send_num[qq_id] = send_num.pop(old_id, 0)
                                if old_id in bot_avatar_cache:
                                    bot_avatar_cache[qq_id] = bot_avatar_cache.pop(old_id)
                                logger.info(f"Bot ID updated: {old_id} -> {qq_id}")
                    except Exception as e:
                        logger.debug(f"Failed to get_login_info: {e}")

                    try:
                        status = await client.api.call_action("get_status")
                        if status and isinstance(status, dict):
                            data = status.get("data", {})
                            if isinstance(data, dict):
                                for key in ["start_time", "boot_time", "online_time", "startTime", "good"]:
                                    if key in data:
                                        val = data[key]
                                        if key == "good" and isinstance(val, bool):
                                            continue
                                        if isinstance(val, (int, float)) and val > 1000000000:
                                            real_connect_time = datetime.fromtimestamp(val).astimezone()
                                            logger.info(f"Got real connect time from protocol: {real_connect_time}")
                                            break
                    except Exception as e:
                        logger.debug(f"Failed to get_status for connect time: {e}")
        except Exception as e:
            logger.debug(f"Error fetching bot info from platform: {e}")

        if config_module.config.ps_use_env_nick:
            nick = self.fallback_nick
            logger.debug(f"ps_use_env_nick enabled, using fallback nick: {nick}")

        try:
            if platform_name == "aiocqhttp" and self._bot_id and self._bot_id != "0" and self._bot_id != "default":
                avatar_bytes = await fetch_qq_avatar(self._bot_id, timeout=config_module.config.ps_req_timeout or 10)
        except Exception as e:
            logger.debug(f"Failed to fetch avatar: {e}")

        if real_connect_time is not None:
            bot_connect_time[self._bot_id] = real_connect_time
            logger.info(f"Updated connect time to protocol start time: {real_connect_time}")

        bot_info_cache[self._bot_id] = {
            "self_id": self._bot_id,
            "nick": nick,
            "name": nick,
            "id": self._bot_id,
        }
        if avatar_bytes:
            bot_avatar_cache[self._bot_id] = avatar_bytes
            logger.info(f"Cached avatar for bot {self._bot_id}")

        bot_info_fetched = True
        logger.info(f"Bot info finalized: id={self._bot_id}, nick={nick}")

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_all_message(self, event: AstrMessageEvent):
        global_config = config_module.config
        text = event.message_str.strip()

        recv_num[self._bot_id] = recv_num.get(self._bot_id, 0) + 1

        if not bot_info_fetched:
            try:
                await self._fetch_bot_info(event)
            except Exception as e:
                logger.debug(f"Failed to fetch bot info: {e}")

        if text not in global_config.ps_command:
            return

        if global_config.ps_need_at:
            is_at_me = False
            msg_obj = getattr(event, "message_obj", None)
            if msg_obj and hasattr(msg_obj, "message"):
                for comp in msg_obj.message:
                    if isinstance(comp, At):
                        target = str(getattr(comp, "qq", getattr(comp, "target", "")))
                        if target == self._bot_id:
                            is_at_me = True
                            break
            if not is_at_me:
                return

        if global_config.ps_only_su:
            is_admin = False
            if hasattr(event, "is_admin"):
                is_admin = event.is_admin()
            elif hasattr(event, "role"):
                is_admin = event.role in ("admin", "owner")
            if not is_admin:
                return

        result = await self._build_status_result(event)
        yield result

    @filter.after_message_sent()
    async def on_after_message_sent(self, event: AstrMessageEvent):
        bot_id = getattr(event, "self_id", None)
        if not bot_id and hasattr(event, "session"):
            bot_id = getattr(event.session, "self_id", self._bot_id)
        bot_id = str(bot_id or self._bot_id)

        send_num[self._bot_id] = send_num.get(self._bot_id, 0) + 1
        logger.debug(f"Message sent counted, total={send_num[self._bot_id]}")

    async def _build_status_result(self, event: AstrMessageEvent):
        if self._bot_id not in bot_connect_time:
            bot_connect_time[self._bot_id] = _process_create_time
        if self._bot_id not in bot_info_cache:
            bot_info_cache[self._bot_id] = {
                "self_id": self._bot_id,
                "nick": self.fallback_nick,
                "name": self.fallback_nick,
                "id": self._bot_id,
            }

        try:
            bg, collected = await asyncio.gather(bg_preloader.get(), collect_all())
            ret = await render_current_template(collected=collected, bg=bg)
        except Exception:
            logger.exception("获取运行状态图失败")
            return event.plain_result("获取运行状态图片失败，请检查后台输出")

        chain = [Image.fromBytes(ret)]
        return event.chain_result(chain)
