"""Save/load system — multi-slot JSON persistence for pet state + session data."""
import json
import os
import shutil
from settings import SAVE_FILENAME, MAX_SAVE_SLOTS, SAVES_DIR

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_LEGACY_MIGRATED = False


def _saves_dir():
    return os.path.join(_BASE_DIR, SAVES_DIR)


def _slot_path(slot):
    return os.path.join(_saves_dir(), f"slot_{slot}.json")


def _ensure_saves_dir():
    d = _saves_dir()
    if not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)


def migrate_legacy_save():
    """Move old single-file save to slot 1 if it exists. Runs once per session."""
    global _LEGACY_MIGRATED
    if _LEGACY_MIGRATED:
        return
    _LEGACY_MIGRATED = True
    legacy = os.path.join(_BASE_DIR, SAVE_FILENAME)
    if os.path.exists(legacy):
        _ensure_saves_dir()
        dest = _slot_path(1)
        if not os.path.exists(dest):
            shutil.move(legacy, dest)
        else:
            os.remove(legacy)


def list_saves():
    """Return a list of MAX_SAVE_SLOTS entries. Each is None (empty) or
    {"slot": N, "name": str, "pet_type": str, "date": str}."""
    migrate_legacy_save()
    result = []
    for slot in range(1, MAX_SAVE_SLOTS + 1):
        path = _slot_path(slot)
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                pet = data.get("pet", {})
                result.append({
                    "slot": slot,
                    "name": pet.get("name", "???"),
                    "pet_type": pet.get("pet_type", "cat"),
                    "date": data.get("last_session_date", ""),
                })
            except (json.JSONDecodeError, KeyError):
                result.append(None)
        else:
            result.append(None)
    return result


def save_game(slot, pet, session_date=None):
    """Save pet state to a numbered slot (1-based)."""
    _ensure_saves_dir()
    data = {"pet": pet.to_dict()}
    if session_date:
        data["last_session_date"] = session_date
    with open(_slot_path(slot), "w") as f:
        json.dump(data, f, indent=2)


def load_game(slot):
    """Load and return save data dict from a slot, or None."""
    migrate_legacy_save()
    path = _slot_path(slot)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def delete_save(slot):
    """Delete a save slot file."""
    path = _slot_path(slot)
    if os.path.exists(path):
        os.remove(path)


def find_empty_slot():
    """Return the first empty slot number (1-based), or None if all full."""
    migrate_legacy_save()
    for slot in range(1, MAX_SAVE_SLOTS + 1):
        if not os.path.exists(_slot_path(slot)):
            return slot
    return None


def has_any_save():
    """Return True if any save slot is occupied."""
    migrate_legacy_save()
    for slot in range(1, MAX_SAVE_SLOTS + 1):
        if os.path.exists(_slot_path(slot)):
            return True
    return False
