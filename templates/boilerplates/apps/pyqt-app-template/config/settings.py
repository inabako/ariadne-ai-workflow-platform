from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "pyqt-app-template"
    robot_host: str = "127.0.0.1"
    udp_control_port: int = 5005
    udp_telemetry_port: int = 5007
    udp_announce_port: int = 5006
    video_port: int = 5600
    enable_discovery: bool = False
    enable_gstreamer: bool = False
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_name=os.getenv("APP_NAME", cls.app_name),
            robot_host=os.getenv("ROBOT_HOST", cls.robot_host),
            udp_control_port=_env_int("UDP_CONTROL_PORT", cls.udp_control_port),
            udp_telemetry_port=_env_int("UDP_TELEMETRY_PORT", cls.udp_telemetry_port),
            udp_announce_port=_env_int("UDP_ANNOUNCE_PORT", cls.udp_announce_port),
            video_port=_env_int("VIDEO_PORT", cls.video_port),
            enable_discovery=_env_bool("ENABLE_DISCOVERY", cls.enable_discovery),
            enable_gstreamer=_env_bool("ENABLE_GSTREAMER", cls.enable_gstreamer),
            log_level=os.getenv("LOG_LEVEL", cls.log_level),
        )


def _env_int(key: str, fallback: int) -> int:
    value = os.getenv(key)
    if value is None:
        return fallback
    try:
        return int(value)
    except ValueError:
        return fallback


def _env_bool(key: str, fallback: bool) -> bool:
    value = os.getenv(key)
    if value is None:
        return fallback
    return value.lower() in {"1", "true", "yes", "on"}
