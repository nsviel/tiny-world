"""Command-line arguments for the interactive application."""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(slots=True)
class ApplicationArguments:
    agent: str
    seed: int
    replay: Path | None


def parse_arguments(argv: Sequence[str] | None = None) -> ApplicationArguments:
    """Parse the interactive application's command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the TinyWorld AI simulation")
    parser.add_argument("--agent", choices=("rule", "random"), default="rule")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--replay", type=Path, help="JSON replay file to save")
    namespace = parser.parse_args(argv)
    return ApplicationArguments(
        agent=namespace.agent,
        seed=namespace.seed,
        replay=namespace.replay,
    )
