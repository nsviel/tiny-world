"""Minimal example of a user-defined TinyWorld agent."""

from tinyworld import Action, Observation, TinyWorldEnv
from tinyworld.agents import BaseAgent


class CustomAgent(BaseAgent):
    """Eat food underfoot and otherwise keep moving forward."""

    def reset(self, seed: int | None = None) -> None:
        """This stateless policy has no episode state to reset."""
        del seed

    def act(self, observation: Observation) -> Action:
        centre = observation.local_grid.shape[1] // 2
        if observation.local_grid[1, centre, centre] > 0.5:
            return Action.EAT
        return Action.MOVE_FORWARD


def main() -> None:
    """Run one short headless episode."""
    env = TinyWorldEnv(seed=0)
    agent = CustomAgent()
    observation, _ = env.reset(seed=0)
    agent.reset(seed=0)
    for _ in range(25):
        action = agent.act(observation)
        observation, _, terminated, truncated, _ = env.step(action)
        if terminated or truncated:
            break


if __name__ == "__main__":
    main()
