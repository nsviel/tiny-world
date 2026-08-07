"""Headless command-line evaluation for TinyWorld agents."""

from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from secrets import randbits

from src.agents import BaseAgent, RandomAgent, RuleBasedAgent
from src.world.environment.env import TinyWorldEnv

from .config import SimulationConfig

from .metrics import EpisodeAggregate, EpisodeMetrics, aggregate_episodes

_AGENT_TYPES: dict[str, Callable[[int | None], BaseAgent]] = {
    "random": RandomAgent,
    "rule": RuleBasedAgent,
}


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"expected an integer, got {value!r}") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def _seed(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"expected an integer, got {value!r}") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("seed must be non-negative")
    return parsed


def evaluate(
    agent: str | BaseAgent,
    *,
    episodes: int = 100,
    seed: int = 0,
    max_steps: int = 500,
) -> EpisodeAggregate:
    """Evaluate an agent over deterministic episode seeds, without rendering.

    Episode ``i`` uses ``seed + i`` for both the world and the agent. Passing an
    agent instance is useful for custom programmatic evaluations; named agents
    accepted by the CLI are ``"rule"`` and ``"random"``.
    """
    if episodes <= 0:
        raise ValueError("episodes must be greater than zero")
    if seed < 0:
        raise ValueError("seed must be non-negative")
    if max_steps <= 0:
        raise ValueError("max_steps must be greater than zero")

    if isinstance(agent, str):
        try:
            policy = _AGENT_TYPES[agent](seed)
        except KeyError as exc:
            choices = ", ".join(sorted(_AGENT_TYPES))
            raise ValueError(f"unknown agent {agent!r}; expected one of: {choices}") from exc
    elif isinstance(agent, BaseAgent):
        policy = agent
    else:
        raise TypeError("agent must be 'rule', 'random', or a BaseAgent instance")

    env = TinyWorldEnv(simulation_config=SimulationConfig(max_steps=max_steps), seed=seed)
    results: list[EpisodeMetrics] = []
    for episode_index in range(episodes):
        # Derive reproducible, distinct episode streams.
        episode_seed = seed + episode_index
        observation, _ = env.reset(seed=episode_seed)
        policy.reset(seed=episode_seed)
        total_reward = 0.0

        while True:
            observation, reward, terminated, truncated, _ = env.step(policy.act(observation))
            total_reward += reward
            if terminated or truncated:
                break

        results.append(EpisodeMetrics.from_env(env, total_reward))

    return aggregate_episodes(results)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate a TinyWorld agent without rendering.")
    parser.add_argument("--agent", choices=sorted(_AGENT_TYPES), required=True)
    parser.add_argument("--episodes", type=_positive_int, default=100)
    parser.add_argument(
        "--seed",
        type=_seed,
        default=None,
        help="base seed (generated when omitted)",
    )
    parser.add_argument("--max-steps", type=_positive_int, default=500)
    return parser


def _format_summary(summary: EpisodeAggregate) -> str:
    return "\n".join(
        (
            f"Survie: {summary.survival_time.mean:.2f} ± {summary.survival_time.std:.2f}",
            f"Nourriture: {summary.food_collected.mean:.2f} ± {summary.food_collected.std:.2f}",
            f"Énergie finale: {summary.final_energy.mean:.2f} ± {summary.final_energy.std:.2f}",
            f"Mortalité: {summary.deaths}/{summary.episodes} ({summary.mortality_rate:.2%})",
            f"Récompense: {summary.total_reward.mean:.2f} ± {summary.total_reward.std:.2f}",
        )
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the evaluation CLI and return a process exit status."""
    args = _parser().parse_args(argv)
    base_seed = args.seed if args.seed is not None else randbits(63)
    print(f"Graine de base: {base_seed}")
    summary = evaluate(
        args.agent,
        episodes=args.episodes,
        seed=base_seed,
        max_steps=args.max_steps,
    )
    print(_format_summary(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
