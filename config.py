import shutil
from pathlib import Path
from typing import Literal, List, Optional
from pydantic import BaseModel

RES_PATH = Path(__file__).parent / "res"
ASSETS_PATH = RES_PATH / "assets"
TEMPLATE_PATH = RES_PATH / "templates"
DEFAULT_BG_PATH = ASSETS_PATH / "default_bg_0.webp"
DEFAULT_AVATAR_PATH = ASSETS_PATH / "default_avatar.webp"

CACHE_DIR = Path(__file__).parent / ".cache"
BG_PRELOAD_CACHE_DIR = CACHE_DIR / "bg_preload"
if BG_PRELOAD_CACHE_DIR.exists():
    shutil.rmtree(BG_PRELOAD_CACHE_DIR)
BG_PRELOAD_CACHE_DIR.mkdir(parents=True, exist_ok=True)

ProcSortByType = Literal["cpu", "mem"]


class TestSiteCfg(BaseModel):
    name: str
    url: str
    use_proxy: bool = False


class ConfigModel:
    """PicStatus 配置（默认值，如需修改请直接编辑本文件）"""
    ps_template: str = "default"
    ps_command: List[str] = ["状态", "status"]
    ps_only_su: bool = False
    ps_need_at: bool = False
    ps_reply_target: bool = True
    ps_req_timeout: Optional[int] = 10
    ps_bg_provider: str = "local"
    ps_bg_preload_count: int = 2
    ps_bg_local_path: Path = ASSETS_PATH
    ps_default_avatar: Path = DEFAULT_AVATAR_PATH
    ps_collect_interval: int = 5
    ps_default_collect_cache_size: int = 1
    ps_collect_cache_size: dict = {}
    ps_use_env_nick: bool = False
    ps_show_current_bot_only: bool = False
    ps_ignore_parts: List[str] = []
    ps_ignore_bad_parts: bool = False
    ps_sort_parts: bool = True
    ps_sort_parts_reverse: bool = False
    ps_ignore_disk_ios: List[str] = [r"^(loop|zram)\d*$"]
    ps_ignore_no_io_disk: bool = False
    ps_sort_disk_ios: bool = True
    ps_ignore_nets: List[str] = [r"^lo(op)?\d*$|^(Loopback|本地连接)"]
    ps_ignore_0b_net: bool = False
    ps_sort_nets: bool = True
    ps_test_sites: List[TestSiteCfg] = [
        TestSiteCfg(name="百度", url="https://www.baidu.com/"),
        TestSiteCfg(name="Google", url="https://www.google.com/", use_proxy=True),
    ]
    ps_sort_sites: bool = True
    ps_test_timeout: int = 3
    proxy: Optional[str] = None
    ps_proc_len: int = 5
    ps_ignore_procs: List[str] = ["^System Idle Process$"]
    ps_proc_sort_by: ProcSortByType = "cpu"
    ps_proc_cpu_max_100p: bool = False
    ps_default_components: List[str] = ["header", "cpu_mem", "disk", "network", "process", "footer"]
    ps_default_pic_format: str = "jpeg"
    ps_default_use_periodic: bool = True


config: ConfigModel = ConfigModel()
