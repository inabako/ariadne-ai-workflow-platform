from __future__ import annotations

import os


class DiscordTokenProvider:
    def __init__(self, env_name: str = "DISCORD_BOT_TOKEN") -> None:
        self.env_name = env_name

    def get_token(self) -> str:
        token = os.environ.get(self.env_name, "")
        if not token:
            raise RuntimeError(f"{self.env_name} is not set")
        return token


def escape_mentions(text: str) -> str:
    return (
        text.replace("@everyone", "@\u200beveryone")
        .replace("@here", "@\u200bhere")
        .replace("<@", "<@\u200b")
        .replace("<@&", "<@&\u200b")
    )


def mask_token(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"

