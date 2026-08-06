"""Dependency-free episode metrics and aggregation helpers."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from math import fsum, sqrt


@dataclass(frozen=True, slots=True)
class EpisodeMetrics:
    """Metrics collected at the end of one TinyWorld episode."""

    survival_time: int
    food_collected: int
    final_energy: float
    died: bool
    total_reward: float

    @classmethod
    def from_env(cls, env: object, total_reward: float) -> "EpisodeMetrics":
        """Build metrics from a finished (or partially run) TinyWorld environment."""
        agent = getattr(env, "agent")
        return cls(
            survival_time=int(getattr(env, "elapsed_steps")),
            food_collected=int(getattr(agent, "food_eaten")),
            final_energy=float(getattr(agent, "energy")),
            died=not bool(getattr(agent, "alive")),
            total_reward=float(total_reward),
        )

    def to_dict(self) -> dict[str, int | float | bool]:
        return {
            "survival_time": self.survival_time,
            "food_collected": self.food_collected,
            "final_energy": self.final_energy,
            "died": self.died,
            "total_reward": self.total_reward,
        }


@dataclass(frozen=True, slots=True)
class MeanStd:
    """Mean and population standard deviation of a metric."""

    mean: float
    std: float

    def to_dict(self) -> dict[str, float]:
        return {"mean": self.mean, "std": self.std}


@dataclass(frozen=True, slots=True)
class EpisodeAggregate:
    """Aggregate statistics over a collection of episodes."""

    episodes: int
    survival_time: MeanStd
    food_collected: MeanStd
    final_energy: MeanStd
    total_reward: MeanStd
    deaths: int
    mortality_rate: float

    def to_dict(self) -> dict[str, int | float | dict[str, float]]:
        return {
            "episodes": self.episodes,
            "survival_time": self.survival_time.to_dict(),
            "food_collected": self.food_collected.to_dict(),
            "final_energy": self.final_energy.to_dict(),
            "total_reward": self.total_reward.to_dict(),
            "deaths": self.deaths,
            "mortality_rate": self.mortality_rate,
        }


def mean_std(values: Iterable[int | float]) -> MeanStd:
    """Return mean and population standard deviation (``ddof=0``).

    Empty iterables return zeros, which keeps empty experiment summaries useful
    to callers without introducing NaNs into JSON output.
    """
    samples = tuple(float(value) for value in values)
    if not samples:
        return MeanStd(0.0, 0.0)
    mean = fsum(samples) / len(samples)
    variance = fsum((value - mean) ** 2 for value in samples) / len(samples)
    return MeanStd(mean, sqrt(variance))


def aggregate_episodes(episodes: Iterable[EpisodeMetrics]) -> EpisodeAggregate:
    """Aggregate episode metrics into means, standard deviations and mortality."""
    samples: Sequence[EpisodeMetrics] = tuple(episodes)
    deaths = sum(episode.died for episode in samples)
    count = len(samples)
    return EpisodeAggregate(
        episodes=count,
        survival_time=mean_std(episode.survival_time for episode in samples),
        food_collected=mean_std(episode.food_collected for episode in samples),
        final_energy=mean_std(episode.final_energy for episode in samples),
        total_reward=mean_std(episode.total_reward for episode in samples),
        deaths=deaths,
        mortality_rate=deaths / count if count else 0.0,
    )


# A readable alias for experiment/CLI code.
summarize_episodes = aggregate_episodes


__all__ = [
    "EpisodeAggregate",
    "EpisodeMetrics",
    "MeanStd",
    "aggregate_episodes",
    "mean_std",
    "summarize_episodes",
]
