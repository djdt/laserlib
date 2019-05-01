import numpy as np

from .. import __version__

from .error import LaserLibException

from typing import Any, Dict, List
from .. import Laser, LaserCalibration, LaserConfig, LaserData
from ..krisskross import KrissKross, KrissKrossConfig, KrissKrossData


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
    elif npz["version"] < "0.1.1":
        raise LaserLibException(f"Archive version mismatch: {npz['version']}.")

    for f in npz.files:
        if f == "version":
            continue
        data = {}
        laserdict = npz[f].item()
        if laserdict["type"] == "Laser":
            config = LaserConfig(**laserdict["config"])
            for k, v in laserdict["data"].items():
                calibration = LaserCalibration(**laserdict["calibration"][k])
                data[k] = LaserData(v, calibration)
            laser = Laser(data=data, config=config, name=laserdict["name"], filepath=path)
        elif laserdict["type"] == "KrissKross":
            config = KrissKrossConfig(**laserdict["config"])
            for k, v in laserdict["data"].items():
                calibration = LaserCalibration(**laserdict["calibration"][k])
                data[k] = KrissKrossData(v, calibration)
            laser = KrissKross(  # type: ignore
                data=data, config=config, name=laserdict["name"], filepath=path
            )
        else:
            raise LaserLibException(f"Unknown laser type {laserdict['type']}!")

        lasers.append(laser)

    return lasers


def save(path: str, laser_list: List[Laser]) -> None:
    savedict: Dict[str, Any] = {"version": __version__}
    for laser in laser_list:
        laserdict = {
            "type": laser.__class__.__name__,
            "name": laser.name,
            "config": laser.config.__dict__,
            "data": {k: v.data for k, v in laser.data.items()},
            "calibration": {k: v.calibration.__dict__ for k, v in laser.data.items()},
        }
        name = laser.name
        if name in savedict:
            i = 0
            while f"{name}{i}" in savedict:
                i += 1
            name += f"{name}{i}"
        savedict[name] = laserdict
    np.savez_compressed(path, **savedict)