# tix/storage/backup.py
from pathlib import Path
from datetime import datetime
import shutil
import json
from typing import Optional, List

def _ensure_backups_dir(storage_path: Path) -> Path:
    """Return the backups directory next to storage_path (create if missing)."""
    backups_dir = storage_path.parent / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    return backups_dir

def _timestamp() -> str:
    """UTC timestamp suitable for filenames: YYYYMMDDTHHMMSSZ"""
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

def _safe_filename(base: Optional[str]) -> str:
    if not base:
        return f"tix-backup-{_timestamp()}.json"
    # take only the stem (no directories, no extension)
    base_stem = Path(base).stem
    return f"{base_stem}-{_timestamp()}.json"

def create_backup(storage_path: Path, filename: Optional[str] = None) -> Path:
    """
    Create a timestamped backup of the given storage_path.
    Returns the Path to created backup file.
    Raises FileNotFoundError if storage_path does not exist.
    Raises OSError for I/O errors.
    """
    storage_path = Path(storage_path)
    if not storage_path.exists():
        raise FileNotFoundError(f"Data file not found: {storage_path}")

    backups_dir = _ensure_backups_dir(storage_path)

    target_name = _safe_filename(filename)
    tmp = backups_dir / (target_name + ".tmp")
    target = backups_dir / target_name

    # copy metadata and contents; copy2 preserves timestamps if possible
    shutil.copy2(storage_path, tmp)
    # atomic replace
    tmp.replace(target)
    return target

def list_backups(storage_path: Path) -> List[Path]:
    """
    Return sorted list of backup files for the given storage_path.
    """
    backups_dir = _ensure_backups_dir(Path(storage_path))
    files = [p for p in backups_dir.iterdir() if p.is_file() and p.suffix == ".json"]
    return sorted(files)

def restore_from_backup(backup_arg: str, storage_path: Path, require_confirm: bool = True) -> Path:
    """
    Restore the named backup into storage_path.
    `backup_arg` may be a filename inside backups/ or an absolute/relative path.
    If require_confirm is True, ask user to confirm via input().
    Returns the path to the restored storage_path.
    Raises FileNotFoundError if backup cannot be located.
    Raises RuntimeError if the user cancels.
    """
    storage_path = Path(storage_path)
    backups_dir = _ensure_backups_dir(storage_path)

    candidate = Path(backup_arg)
    if candidate.exists():
        backup_path = candidate
    else:
        # try to find inside backups dir by name
        byname = backups_dir / candidate.name
        if byname.exists():
            backup_path = byname
        else:
            raise FileNotFoundError(f"Backup not found: {backup_arg}")

    if require_confirm:
        print(f"About to restore backup: {backup_path} -> {storage_path}")
        try:
            resp = input("This will overwrite your current tasks file. Continue? [y/N] ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print()
            raise RuntimeError("Restore cancelled")
        if resp not in ("y", "yes"):
            raise RuntimeError("Restore cancelled by user")

    # ensure parent dir exists for storage file
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = storage_path.with_suffix(storage_path.suffix + ".tmp")
    shutil.copy2(backup_path, tmp)
    tmp.replace(storage_path)
    return storage_path
