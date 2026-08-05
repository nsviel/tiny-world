import numpy as np
import pytest

from src import (
    OBSERVATION_CHANNELS,
    SCALAR_FEATURES,
    Orientation,
    Position,
    Tile,
    TinyWorldEnv,
    WorldConfig,
)


def test_observation_has_expected_shapes_dtypes_and_channels() -> None:
    env = TinyWorldEnv(WorldConfig(view_size=11), seed=23)

    observation, _ = env.reset(seed=23)

    assert OBSERVATION_CHANNELS == ("obstacles", "food", "predator", "agent")
    assert SCALAR_FEATURES == ("energy_norm", "orientation_norm", "food", "time_norm")
    assert observation.local_grid.shape == (4, 11, 11)
    assert observation.scalar_features.shape == (4,)
    assert observation.local_grid.dtype == np.float32
    assert observation.scalar_features.dtype == np.float32
    assert observation.local_grid[3, 5, 5] == 1.0
    assert observation.local_grid[3].sum() == 1.0


def test_scalar_features_encode_energy_orientation_food_and_time() -> None:
    config = WorldConfig(
        width=11,
        height=11,
        food_count=0,
        water_ratio=0.0,
        tree_ratio=0.0,
        initial_energy=80.0,
        max_energy=100.0,
        max_steps=10,
    )
    env = TinyWorldEnv(config, seed=3)
    env.world.tiles.fill(Tile.GROUND)
    env.agent.position = Position(5, 5)
    env.agent.orientation = Orientation.WEST
    env.agent.energy = 50.0
    env.agent.food_eaten = 2
    env.elapsed_steps = 4

    observation = env._observation()

    np.testing.assert_allclose(
        observation.scalar_features,
        np.asarray([0.5, 1.0, 2.0, 0.4], dtype=np.float32),
    )
    assert np.all(np.isin(observation.local_grid, (0.0, 1.0)))


def test_observation_marks_obstacles_food_and_predator_relative_to_agent() -> None:
    env = TinyWorldEnv(
        WorldConfig(width=11, height=11, food_count=0, water_ratio=0.0, tree_ratio=0.0),
        seed=5,
    )
    env.world.tiles.fill(Tile.GROUND)
    env.agent.position = Position(5, 5)
    env.world.tiles[4, 5] = Tile.WATER
    env.world.tiles[5, 6] = Tile.FOOD
    env.world.predator.position = Position(6, 5)

    observation = env._observation()

    assert observation.local_grid[0, 4, 5] == 1.0
    assert observation.local_grid[1, 5, 6] == 1.0
    assert observation.local_grid[2, 6, 5] == 1.0
    assert observation.local_grid[3, 5, 5] == 1.0
    assert observation.scalar_features[0] == pytest.approx(1.0)
