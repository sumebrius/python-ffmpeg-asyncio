from datetime import timedelta

from ffmpeg_asyncio.stats import Statistics


def test_stats_line_parsing():
    sample_lines = [
        # ffmpeg version 6
        "frame=   10 fps=7.0 q=-1.0 Lsize=    8733kB time=00:00:03.00 bitrate=23832.3kbits/s speed= 106x",
        # ffmpeg version 7
        "frame=   10 fps=7.0 q=-1.0 Lsize=    8733KiB time=00:00:03.00 bitrate=23832.3kbits/s speed= 106x",
    ]

    sample_lines_no_frame = [
        # ffmpeg version 6
        "size=    8733kB time=00:00:03.00 bitrate=23832.3kbits/s speed= 106x",
        # ffmpeg version 7
        "size=    8733KiB time=00:00:03.00 bitrate=23832.3kbits/s speed= 106x",
    ]

    for line in sample_lines:
        assert Statistics.from_line(line) == Statistics(
            frame=10,
            fps=7.0,
            size=8_942_592,
            time=timedelta(seconds=3),
            bitrate=23832.3,
            speed=106,
        )

    for line in sample_lines_no_frame:
        assert Statistics.from_line(line) == Statistics(
            frame=0,
            fps=0.0,
            size=8_942_592,
            time=timedelta(seconds=3),
            bitrate=23832.3,
            speed=106,
        )


def test_na_exclusion():
    stats = Statistics.from_line(
        "size=       N/A time=00:00:03.00 bitrate=23832.3kbits/s speed=  N/A",
    )
    assert stats.size == 0
    assert stats.speed == 0.0
