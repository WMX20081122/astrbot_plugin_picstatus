from typing import TYPE_CHECKING
from ..util import auto_convert_byte, format_cpu_freq

if TYPE_CHECKING:
    import jinja2


jinja_filters = {}


def register_global_filter_to(env: "jinja2.Environment"):
    env.filters.update(jinja_filters)


def jinja_filter(func):
    jinja_filters[func.__name__] = func
    return func


@jinja_filter
def percent_to_color(percent: float) -> str:
    if percent < 70:
        return "prog-low"
    if percent < 90:
        return "prog-medium"
    return "prog-high"


@jinja_filter
def auto_convert_unit(value: float, **kw) -> str:
    return auto_convert_byte(value=value, with_space=False, **kw)


jinja_filter(format_cpu_freq)
