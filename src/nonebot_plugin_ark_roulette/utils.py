import json
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

R_contra = TypeVar("R_contra", contravariant=True)


def require_json(*jsons: str | Path):
    def __inner_require_json(func: Callable[..., R_contra]) -> Callable[[], R_contra]:
        paths = [Path(f) for f in jsons]
        def __wrapped_require_json() -> R_contra:
            data = [json.loads(p.read_text()) for p in paths]
            return func(*data)

        return __wrapped_require_json

    return __inner_require_json
