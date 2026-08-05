import pytest

from src import Action, Orientation, Position, Tile, TinyWorldEnv, WorldConfig
from src.agents import RandomAgent, RuleBasedAgent


def controlled_env(**overrides: object) -> TinyWorldEnv:
    values: dict[str, object] = {
        "width": 11,
        "height": 11,
        "food_count": 0,
        "water_ratio": 0.0,
        "tree_ratio": 0.0,
        "predator_detection_radius": 0,
        "max_steps": 100,
    }
    values.update(overrides)
    env = TinyWorldEnv(WorldConfig(**values), seed=7)
    env.world.tiles.fill(Tile.GROUND)
    env.agent.position = Position(5, 5)
    env.agent.orientation = Orientation.NORTH
    env.world.predator.position = Position(9, 9)
    return env


def test_obstacle_is_impassable_and_move_still_costs_energy() -> None:
    env = controlled_env()
    env.world.tiles[4, 5] = Tile.TREE
    start = env.agent.position
    energy = env.agent.energy

    _, _, terminated, truncated, info = env.step(Action.MOVE_FORWARD)

    assert env.agent.position == start
    assert env.agent.energy == pytest.approx(energy - env.config.move_cost)
    assert info["events"].invalid_action is True
    assert not terminated
    assert not truncated


def test_energy_decreases_for_an_action() -> None:
    env = controlled_env()
    energy = env.agent.energy

    env.step(Action.TURN_RIGHT)

    assert env.agent.energy == pytest.approx(energy - env.config.turn_cost)


def test_eating_collects_food_and_restores_energy() -> None:
    env = controlled_env()
    env.agent.energy = 50.0
    env.world.tiles[5, 5] = Tile.FOOD

    _, _, terminated, truncated, info = env.step(Action.EAT)

    assert env.world.tiles[5, 5] == Tile.GROUND
    assert env.agent.food_eaten == 1
    assert env.agent.energy == pytest.approx(50.0 + env.config.food_energy - env.config.eat_cost)
    assert info["food_collected"] == 1
    assert info["events"].ate_food is True
    assert not terminated
    assert not truncated


def test_episode_terminates_when_energy_is_exhausted() -> None:
    env = controlled_env(initial_energy=0.1, max_energy=1.0, idle_cost=0.1)

    _, _, terminated, truncated, info = env.step(Action.IDLE)

    assert terminated is True
    assert truncated is False
    assert env.agent.energy == 0.0
    assert env.agent.alive is False
    assert info["events"].died is True


def test_episode_is_truncated_at_time_limit() -> None:
    env = controlled_env(max_steps=2)

    assert env.step(Action.IDLE)[2:4] == (False, False)
    assert env.step(Action.IDLE)[2:4] == (False, True)


@pytest.mark.parametrize("agent_type", [RandomAgent, RuleBasedAgent])
def test_existing_agents_run_1000_total_steps_with_episode_resets(agent_type: type) -> None:
    env = TinyWorldEnv(
        WorldConfig(
            width=11,
            height=11,
            food_count=0,
            water_ratio=0.0,
            tree_ratio=0.0,
            max_steps=20,
        ),
        seed=100,
    )
    agent = agent_type(seed=100)
    observation, _ = env.reset(seed=100)
    agent.reset(seed=100)
    episodes = 0

    for step_index in range(1000):
        action = agent.act(observation)
        assert isinstance(action, Action)
        observation, _, terminated, truncated, _ = env.step(action)
        if terminated or truncated:
            episodes += 1
            episode_seed = 101 + step_index
            observation, _ = env.reset(seed=episode_seed)
            agent.reset(seed=episode_seed)

    assert episodes > 0
