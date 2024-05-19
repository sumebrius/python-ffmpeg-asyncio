# ffmpeg-asyncio

A fork of the excellent [`python-ffmpeg`](https://python-ffmpeg.readthedocs.io) binding for FFmpeg, updated for native async API support only.

The primary difference from the upstream library's async API is handling of abnormal exit by FFmpeg. Rather than raising an exception, an event will be emitted, allowing async handling.

Example usage:

```python
import asyncio

from ffmpeg_asyncio import FFmpeg, Progress


async def main():
    ffmpeg = (
        FFmpeg()
        .input("input.mp4")
        .output("output.mp4")
    )

    @ffmpeg.on("progress")
    def on_progress(progress: Progress):
        print(progress)

    @ffmpeg.on("completed")
    def completed():
        print("Finished!")

    @ffmpeg.on("terminated")
    def exited(return_code: int):
        print("Oh no!")

    await ffmpeg.execute()


if __name__ == "__main__":
    asyncio.run(main())
```
