"""本角色当前唯一播放参数；客户端尚未接入。"""
RUN_FRAME_MS = 60
RUN_COUNT = 16
RUN_LOOP_MS = RUN_FRAME_MS * RUN_COUNT
ACTION_FRAME_MS = {"run": RUN_FRAME_MS, "hit": 40, "attack": 30, "cast": 45}
RUN_TIMING = {
    "status": "user_requested_offline_delivery",
    "defaultLoopMs": RUN_LOOP_MS,
    "frameCount": RUN_COUNT,
    "frameDurationMs": RUN_FRAME_MS,
    "frameDurationsMs": [RUN_FRAME_MS] * RUN_COUNT,
    "timingMode": "uniform",
    "extraEndPauseMs": 0,
    "slowMultiplier": 4,
    "clientValueChanged": False,
}
