# TinyWorld AI

TinyWorld is a small 2D survival environment built with Python, NumPy, and Pygame. An agent explores a procedural map, looks for food, manages its energy, and tries to avoid a predator.

The simulation can run with or without rendering. It currently includes a random agent and a simple rule-based agent. There is no machine learning code yet.

## Install

Python 3.11 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

If you use micromamba:

```bash
micromamba run -n venv pip install -e ".[dev]"
```

## Run

Start the visual simulation:

```bash
python -m src.game.play --agent rule --seed 42
```

Run several episodes without rendering:

```bash
python -m src.game.evaluate --agent rule --episodes 100 --seed 42
```

Save and watch a replay:

```bash
python -m src.game.play --agent rule --replay run.json
python -m src.engine.replay run.json
```

Use `--agent random` to run the random policy instead.

## Controls

| Key | Action |
|---|---|
| `Space` | Pause |
| `R` | Restart |
| `O` | Show the agent's observation area |
| `C` | Center the camera on the agent |
| Arrow keys | Move the camera |
| Mouse wheel | Zoom |
| Right mouse drag | Move the camera |
| `+` / `-` | Change simulation speed |
| `1` / `2` | Select random / rule-based agent |

## Environment API

The API follows the usual Gym-style `reset` and `step` pattern, without requiring Gymnasium.

```python
from src import Action, TinyWorldEnv

env = TinyWorldEnv(seed=42)
observation, info = env.reset()

done = False
while not done:
    observation, reward, terminated, truncated, info = env.step(
        Action.MOVE_FORWARD
    )
    done = terminated or truncated

env.close()
```

Available actions are `IDLE`, `MOVE_FORWARD`, `TURN_LEFT`, `TURN_RIGHT`, and `EAT`.

An observation contains:

- `local_grid`: a `(4, 11, 11)` NumPy array with obstacle, food, predator, and agent channels;
- `scalar_features`: energy, orientation, collected food, and elapsed time.

## Tests

```bash
pytest
```

The tests cover reproducibility, observations, movement, energy, food collection, episode endings, and both built-in agents.

## License

MIT
