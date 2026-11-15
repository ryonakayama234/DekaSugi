"""Exclusive canonical artifacts and cooperative, attributed resource accounting."""
from contextlib import contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path
import re

from .foundation import Fault, Meter, canonical


def digest(value):
    return sha256(canonical(value)).hexdigest()


@contextmanager
def attributed(meter, scope):
    first = len(meter.receipts)
    try:
        yield
    finally:
        for receipt in meter.receipts[first:]:
            if "scope" in receipt:
                raise Fault("double cost attribution")
            receipt["scope"] = scope


class Artifacts:
    def __init__(self, root, meter):
        if type(meter) is not Meter:
            raise Fault("one exact Meter required")
        self.root = Path(root)
        self.meter = meter
        self.index = {}
        with attributed(meter, "shared/artifact-setup"), meter.phase("artifact-setup"):
            meter.checkpoint()
            self.root.parent.mkdir(parents=True, exist_ok=True)
            self.root.mkdir(exist_ok=False)
            os.chmod(self.root, 0o700)

    def _path(self, name):
        if type(name) is not str or not re.fullmatch(r"[A-Za-z0-9_-]+\.(json|md)", name):
            raise Fault("flat bounded artifact name required")
        return self.root / name

    def write(self, name, value, *, retained=None, text=False):
        with attributed(self.meter, "shared/persistence"), self.meter.phase("persist/" + name):
            path = self._path(name)
            self.meter.checkpoint((retained, self.index, value))
            raw = value.encode("utf-8") if text else canonical(value)
            self.meter.checkpoint((retained, self.index, value, raw))
            with path.open("xb") as out:
                out.write(raw)
                out.flush()
                os.fsync(out.fileno())
            item = {"sha256": sha256(raw).hexdigest(), "bytes": len(raw)}
            self.meter.checkpoint((retained, self.index, value, raw, item))
            self.index[name] = item
        return item

    def read(self, name, *, retained=None):
        with attributed(self.meter, "shared/verification"), self.meter.phase("verify/" + name):
            path = self._path(name)
            expected = self.index.get(name)
            if expected is None or path.is_symlink() or not path.is_file():
                raise Fault("missing/unindexed artifact")
            # Refuse growth before allocating; all original artifacts passed size guard.
            if path.stat().st_size != expected["bytes"]:
                raise Fault("changed artifact size")
            self.meter.checkpoint((retained, self.index))
            raw = path.read_bytes()
            self.meter.checkpoint((retained, self.index, raw))
            if sha256(raw).hexdigest() != expected["sha256"]:
                raise Fault("changed artifact hash")
            value = json.loads(raw)
            self.meter.checkpoint((retained, self.index, raw, value))
            if canonical(value) != raw:
                raise Fault("noncanonical artifact")
        return value
