from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional

from typing_extensions import Self

from .utils import parse_time

# Reference: https://github.com/FFmpeg/FFmpeg/blob/release/5.1/fftools/ffmpeg.c#L1507

_field_pattern = re.compile(r"(frame|fps|size|time|bitrate|speed)\s*\=\s*(?!N/A)(\S+)")
_size_suffix = re.compile(r"(k|Ki)B$")
_rate_suffix = re.compile(r"kbits/s$")
_speed_pattern = re.compile(r"x$")

_field_factory = {
    "frame": int,
    "fps": float,
    "size": lambda item: int(re.sub(_size_suffix, "", item)) * 1024,
    "time": parse_time,
    "bitrate": lambda item: float(re.sub(_rate_suffix, "", item)),
    "speed": lambda item: float(re.sub(_speed_pattern, "", item)),
}


@dataclass(frozen=True)
class Statistics:
    frame: Optional[int] = None
    fps: Optional[float] = None
    size: int = 0
    time: timedelta = field(default_factory=timedelta)
    bitrate: float = 0.0
    speed: float = 0.0

    @classmethod
    def from_line(cls, line: str) -> Optional[Self]:
        fields = {key: _field_factory[key](value) for key, value in _field_pattern.findall(line)}
        if not fields:
            return None
        return Statistics(**fields)
