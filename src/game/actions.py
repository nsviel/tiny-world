"""Actions accepted by :class:`src.world.env.TinyWorldEnv`."""

from enum import IntEnum


class Action(IntEnum):
    IDLE = 0
    MOVE_FORWARD = 1
    TURN_LEFT = 2
    TURN_RIGHT = 3
    EAT = 4
