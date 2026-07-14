from __future__ import annotations

import argparse
from pathlib import Path

from .gateway import DiscordGateway
from .models import DiscordInteraction, DiscordSubject


def demo() -> None:
    gateway = DiscordGateway(state_path=Path("workspace/state/demo-gateway.db"))
    interaction = DiscordInteraction(
        interaction_id="demo-1",
        interaction_type="slash_command",
        command_name="health",
        subject=DiscordSubject(user_id="user-demo", guild_id="guild-demo", channel_id="channel-demo"),
    )
    print(gateway.handle_interaction(interaction))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if args.demo:
        demo()


if __name__ == "__main__":
    main()

