"""
Small state/navigation helper functions for Streamlit components.

Extracted from `new_components.py`.

This module must not import Streamlit. It operates on mutable mapping-like
objects such as `st.session_state`, but does not depend on Streamlit itself.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, MutableMapping






def ensure_nav_state(
    state: MutableMapping[str, Any],
    *,
    position_key: str = "nav_position",
    toggle_key: str = "nav_toggle",
    default_position: str = "sidebar",
) -> None:
    """
    Ensure navigation state keys exist.
    """
    if position_key not in state:
        state[position_key] = default_position
        state[toggle_key] = default_position == "top"


def nav_position_from_toggle(toggle_value: bool) -> str:
    """
    Convert nav toggle boolean to position label.
    """
    return "top" if toggle_value else "sidebar"


def set_nav_position_from_toggle(
    state: MutableMapping[str, Any],
    *,
    position_key: str = "nav_position",
    toggle_key: str = "nav_toggle",
) -> str:
    """
    Update nav position from nav toggle and return the new position.
    """
    state[position_key] = nav_position_from_toggle(bool(state.get(toggle_key, False)))
    return state[position_key]


def get_inverse_toggle_keys(key_page: str) -> tuple[str, str]:
    """
    Return session keys for paired inverse toggles.
    """
    return f"{key_page}_toggle_a", f"{key_page}_toggle_b"


def ensure_inverse_toggle_state(
    state: MutableMapping[str, Any],
    key_a: str,
    key_b: str,
    default_a: bool = False,
) -> None:
    """
    Ensure two inverse toggle keys exist.
    """
    if key_a not in state:
        state[key_a] = default_a

    if key_b not in state:
        state[key_b] = not default_a


def sync_inverse_toggle_state(
    state: MutableMapping[str, Any],
    key_a: str,
    key_b: str,
    changed_key: str,
) -> None:
    """
    Keep paired toggles inverse to each other.

    changed_key should be "a" or "b".
    """
    if changed_key == "a":
        state[key_b] = not bool(state[key_a])
    elif changed_key == "b":
        state[key_a] = not bool(state[key_b])
    else:
        raise ValueError("changed_key must be 'a' or 'b'")


def ensure_index_state(
    state: MutableMapping[str, Any],
    idx_key: str,
    default: int = 0,
) -> None:
    """
    Ensure a numeric index exists in state.
    """
    if idx_key not in state:
        state[idx_key] = default


def shortcut_action_to_nav_action(shortcut_action: dict[str, Any] | None) -> str | None:
    """
    Convert keyboard-shortcut component payload to "prev"/"next".
    """
    if not shortcut_action:
        return None

    action_value = str(shortcut_action.get("action", ""))
    if action_value.startswith("btn_prev_"):
        return "prev"
    if action_value.startswith("btn_next_"):
        return "next"
    return None


def next_prev_index(
    current_pos: int,
    total_items: int,
    action: str | None,
) -> tuple[int, bool]:
    """
    Compute next/previous index.

    Returns:
    - new_pos
    - changed
    """
    if action == "prev" and current_pos > 0:
        return current_pos - 1, True

    if action == "next" and current_pos < total_items - 1:
        return current_pos + 1, True

    return current_pos, False
