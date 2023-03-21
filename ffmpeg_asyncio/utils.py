from __future__ import annotations

import asyncio
import io
import re
import subprocess
import sys
from collections.abc import AsyncIterable, Awaitable
from datetime import timedelta
from typing import IO, Any

from . import types


def parse_time(time: str) -> timedelta:
    match = re.search(r"(-?\d+):(\d+):(\d+)\.(\d+)", time)
    assert match is not None

    return timedelta(
        hours=int(match.group(1)),
        minutes=int(match.group(2)),
        seconds=int(match.group(3)),
        milliseconds=int(match.group(4)) * 10,
    )


def is_windows() -> bool:
    return sys.platform == "win32"


def create_subprocess(*args: Any, **kwargs: Any) -> Awaitable[asyncio.subprocess.Process]:
    # On Windows, CREATE_NEW_PROCESS_GROUP flag is required to use CTRL_BREAK_EVENT signal,
    # which is required to gracefully terminate the FFmpeg process.
    # Reference: https://docs.python.org/3/library/asyncio-subprocess.html#asyncio.subprocess.Process.send_signal
    if is_windows():
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore

    return asyncio.create_subprocess_exec(*args, **kwargs)


async def ensure_stream_reader(stream: types.AsyncStream) -> asyncio.StreamReader:
    if isinstance(stream, asyncio.StreamReader):
        return stream

    reader = asyncio.StreamReader()
    reader.feed_data(stream)
    reader.feed_eof()

    return reader


async def read_stream(stream: asyncio.StreamReader, size: int = -1) -> AsyncIterable[bytes]:
    while not stream.at_eof():
        chunk = await stream.read(size)
        if not chunk:
            break

        yield chunk


async def readlines(stream: asyncio.StreamReader) -> AsyncIterable[bytes]:
    pattern = re.compile(rb"[\r\n]+")

    buffer = bytearray()
    async for chunk in read_stream(stream, io.DEFAULT_BUFFER_SIZE):
        buffer.extend(chunk)

        lines = pattern.split(buffer)
        buffer[:] = lines.pop(-1)  # keep the last line that could be partial

        for line in lines:
            yield line

    if buffer:
        yield bytes(buffer)
