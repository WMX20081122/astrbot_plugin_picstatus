from dataclasses import dataclass
from typing import cast

import psutil
from cpuinfo import get_cpu_info
from astrbot.api import logger

from . import first_time_collector, normal_collector, periodic_collector


@dataclass
class CpuFreq:
    current: float | None
    min: float | None
    max: float | None


@first_time_collector()
async def cpu_brand() -> str:
    try:
        brand = (
            cast("str", get_cpu_info().get("brand_raw", ""))
            .split("@", maxsplit=1)[0]
            .strip()
        )
        if brand.lower().endswith(("cpu", "processor")):
            brand = brand.rsplit(maxsplit=1)[0].strip()
    except Exception:
        logger.exception("Error when getting CPU brand")
        return "未知型号"
    else:
        return brand


@first_time_collector()
async def cpu_count_logical() -> int | None:
    return psutil.cpu_count()


@first_time_collector()
async def cpu_count() -> int | None:
    return psutil.cpu_count(logical=False)


async def get_cpu_percent() -> float:
    val = psutil.cpu_percent(interval=None)
    if val == 0.0:
        import asyncio
        await asyncio.sleep(0.2)
        val = psutil.cpu_percent(interval=None)
    return val


normal_collector("cpu_percent")(get_cpu_percent)
periodic_collector("cpu_percent_periodic")(get_cpu_percent)


async def get_cpu_freq() -> CpuFreq:
    cpu_freq = psutil.cpu_freq()
    return CpuFreq(
        current=getattr(cpu_freq, "current", None),
        min=getattr(cpu_freq, "min", None),
        max=getattr(cpu_freq, "max", None),
    )


normal_collector("cpu_freq")(get_cpu_freq)
periodic_collector("cpu_freq_periodic")(get_cpu_freq)
