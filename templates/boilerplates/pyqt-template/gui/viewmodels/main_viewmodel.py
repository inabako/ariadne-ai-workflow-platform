from __future__ import annotations

from models.telemetry import Telemetry
from services.interfaces import RobotControllerInterface, TelemetryServiceInterface, VideoServiceInterface


class MainViewModel:
    def __init__(
        self,
        robot_controller: RobotControllerInterface,
        telemetry_service: TelemetryServiceInterface,
        video_service: VideoServiceInterface,
    ) -> None:
        self.robot_controller = robot_controller
        self.telemetry_service = telemetry_service
        self.video_service = video_service
        self.last_status = "idle"

    def stop_robot(self) -> None:
        self.robot_controller.send_command("STOP")
        self.last_status = "stop sent"

    def ping_robot(self) -> None:
        self.robot_controller.send_command("PING")
        self.last_status = "ping sent"

    def telemetry(self) -> Telemetry:
        return self.telemetry_service.current()

    def video_label(self) -> str:
        return self.video_service.current_frame_label()
