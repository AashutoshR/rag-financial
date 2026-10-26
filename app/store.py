"""Content-addressed immutable blob store [EXT-01]."""
import hashlib
from pathlib import Path

from app.config import BLOBS


def put(data: bytes) -> tuple[str, Path, bool]:
    """Store bytes under their SHA-256. Returns (sha256, path, created). Identical bytes are a no-op."""
    sha = hashlib.sha256(data).hexdigest()
    path = BLOBS / sha[:2] / sha
    if path.exists():
        return sha, path, False
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)
    return sha, path, True


def path_for(sha: str) -> Path:
    return BLOBS / sha[:2] / sha
