import numpy as np

from .. import __version__

from .error import LaserLibException

from typing import Any, Dict, List
from ..laser import Laser


def load(path: str) -> List[Laser]:
    """Imports the given numpy archive given, returning a list of data.

    Both the config and calibration read from the archive may be overriden.

    Args:
        path: Path to numpy archive
        config_override: If not None will be applied to all imports
        calibration_override: If not None will be applied to all imports

    Returns:
        List of LaserData and KrissKrossData

    Raises:
        PewPewFileError: Version of archive missing or incompatable.

    """
    lasers: List[Laser] = []
    npz = np.load(path)

    if "version" not in npz.files:
        raise LaserLibException("Archive version mismatch.")
    elif npz["version"] < "0.1.0":
        raise LaserLibException(f"Archive version mismatch: {npz['version']}.")

    for f in npz.files:
        if f == "version":
            continue
        lasers.append(npz[f].item())

    return lasers


def save(path: str, laser_list: List[Laser]) -> None:
    savedict: Dict[str, Any] = {
        "version": __version__,
    }
    for laser in laser_list:
        name = laser.name
        if name in savedict:
            i = 0
            while f"{name}{i}" in savedict:
                i += 1
            name += f"{name}{i}"
        savedict[name] = laser
    np.savez_compressed(path, **savedict)
