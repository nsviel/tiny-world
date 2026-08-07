import numpy as np

from src import Action, SimulationConfig, TinyWorldEnv


def assert_observations_equal(first: object, second: object) -> None:
    np.testing.assert_array_equal(first.local_grid, second.local_grid)
    np.testing.assert_array_equal(first.scalar_features, second.scalar_features)


def test_same_seed_reproduces_terrain_and_spawns() -> None:
    first = TinyWorldEnv(seed=12345)
    second = TinyWorldEnv(seed=12345)

    np.testing.assert_array_equal(first.world.tiles, second.world.tiles)
    assert first.world.spawn_position == second.world.spawn_position
    assert first.world.predator.position == second.world.predator.position
    assert first.agent.position == second.agent.position


def test_reset_with_same_seed_restores_identical_world() -> None:
    env = TinyWorldEnv(seed=91)
    original_tiles = env.world.tiles.copy()
    original_spawn = env.world.spawn_position
    original_predator = env.world.predator.position
    env.step(Action.TURN_RIGHT)
    env.step(Action.IDLE)

    observation, info = env.reset(seed=91)

    np.testing.assert_array_equal(env.world.tiles, original_tiles)
    assert env.world.spawn_position == original_spawn
    assert env.agent.position == original_spawn
    assert env.world.predator.position == original_predator
    assert info["seed"] == 91
    assert observation.scalar_features[3] == 0.0


def test_same_seed_and_actions_reproduce_every_transition() -> None:
    config = SimulationConfig(max_steps=50)
    first = TinyWorldEnv(simulation_config=config, seed=2026)
    second = TinyWorldEnv(simulation_config=config, seed=2026)
    actions = (
        Action.IDLE,
        Action.TURN_RIGHT,
        Action.MOVE_FORWARD,
        Action.EAT,
        Action.TURN_LEFT,
        Action.MOVE_FORWARD,
        Action.IDLE,
    ) * 3

    for action in actions:
        transition_a = first.step(action)
        transition_b = second.step(action)
        observation_a, reward_a, terminated_a, truncated_a, info_a = transition_a
        observation_b, reward_b, terminated_b, truncated_b, info_b = transition_b

        assert_observations_equal(observation_a, observation_b)
        assert reward_a == reward_b
        assert (terminated_a, truncated_a) == (terminated_b, truncated_b)
        assert info_a == info_b
        np.testing.assert_array_equal(first.world.tiles, second.world.tiles)
        assert first.agent == second.agent
        assert first.world.predator == second.world.predator
        if terminated_a or truncated_a:
            break
