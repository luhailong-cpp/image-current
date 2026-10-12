"""User-selected 960 ms run cycle: sixteen distinct frames, uniform 60 ms."""
RUN_FRAME_MS = 60
RUN_CYCLE_MS = 960
RUN_NORMAL_DURATIONS = [RUN_FRAME_MS] * 16
assert len(RUN_NORMAL_DURATIONS) == 16 and sum(RUN_NORMAL_DURATIONS) == RUN_CYCLE_MS
