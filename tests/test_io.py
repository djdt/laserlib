import pytest
import os.path
import tempfile
import filecmp
import numpy as np
from pew import io


def test_io_agilent():
    data_path = os.path.join(os.path.dirname(__file__), "data", "agilent")
    # Test loading 7700
    data = io.agilent.load(os.path.join(data_path, "7700.b"))
    assert data.shape == (3, 3)
    assert data.dtype.names == ("A1", "B2")
    assert np.sum(data["A1"]) == pytest.approx(9.0)
    assert np.sum(data["B2"]) == pytest.approx(0.9)
    # Test loading from 7500
    data = io.agilent.load(os.path.join(data_path, "7500.b"))
    assert data.shape == (3, 3)
    assert data.dtype.names == ("A1", "B2")
    assert np.sum(data["A1"]) == pytest.approx(9.0)
    assert np.sum(data["B2"]) == pytest.approx(0.9)
    # Make sure error raised on missing data
    with pytest.raises(io.error.PewException):
        io.agilent.load(os.path.join(data_path, "missing_line.b"))


def test_io_csv():
    data_path = os.path.join(os.path.dirname(__file__), "data", "csv")
    data_path_thermo = os.path.join(os.path.dirname(__file__), "data", "thermo")
    # Make sure error raised on thermo data
    with pytest.raises(io.error.PewException):
        io.csv.load(os.path.join(data_path_thermo, "icap.csv"))
    # Test loading
    data = io.csv.load(os.path.join(data_path, "csv.csv"))
    assert data.dtype.names == ("CSV",)
    assert data.shape == (20, 5)
    assert np.sum(data["CSV"]) == pytest.approx(100.0)
    # Test saving
    temp = tempfile.NamedTemporaryFile()
    data = np.random.random([10, 10])
    data.dtype = [("CSV", float)]
    io.csv.save(temp.name, data["CSV"])
    assert np.all(data["CSV"] == io.csv.load(temp.name)["CSV"])
    temp.close()
    # Delimiter loading
    data = io.csv.load(os.path.join(data_path, "delimiters.csv"))
    assert data.dtype.names == ("CSV",)
    assert data.shape == (10, 5)
    assert np.sum(data["CSV"]) == pytest.approx(100.0)


def test_io_thermo():
    data_path = os.path.join(os.path.dirname(__file__), "data", "thermo")
    data_path_csv = os.path.join(os.path.dirname(__file__), "data", "csv")
    # Make sure csv data raises an error
    with pytest.raises(io.error.PewException):
        io.thermo.load(os.path.join(data_path_csv, "csv.csv"))
    # Test loading
    data = io.thermo.load(os.path.join(data_path, "icap.csv"))
    assert data.shape == (3, 3)
    assert data.dtype.names == ("1A", "2B")
    assert np.sum(data["1A"]) == pytest.approx(9.0)
    assert np.sum(data["2B"]) == pytest.approx(0.9)


def test_io_vtk():
    data_path = os.path.join(os.path.dirname(__file__), "data", "vtk")

    np.random.seed(12718736)
    data = np.random.random((10, 10, 3))
    data.dtype = [("A1", float)]

    temp = tempfile.NamedTemporaryFile(suffix=".vti")
    io.vtk.save(temp.name, data, (1, 1, 1))
    assert filecmp.cmp(temp.name, os.path.join(data_path, "test.vti"))
    temp.close()


# def generate_test_laser():
#     from pew import Laser, Config, Calibration

#     data = np.empty((10, 10), dtype=[("A1", float), ("B2", float)])
#     data["A1"] = np.random.random((10, 10))
#     data["A1"] = data["A1"] / np.sum(data["A1"]) * 100
#     data["B2"] = np.random.random((10, 10))

#     cal_a = Calibration(
#         2.0, 1.0, weighting="x", points=[[1, 1], [2, 2], [3, 3]], unit="test"
#     )

#     laser = Laser(data, calibration={"A1": cal_a}, config=Config(1, 2, 3), name="Test")
#     return laser


def test_io_npz():
    data_path = os.path.join(os.path.dirname(__file__), "data", "npz")
    laser = io.npz.load(os.path.join(data_path, "test.npz"))[0]
    assert laser.name == "Test"
    assert laser.path == os.path.join(data_path, "test.npz")
    # Config
    assert laser.config.spotsize == 1
    assert laser.config.speed == 2
    assert laser.config.scantime == 3
    # Data
    assert laser.isotopes == ("A1", "B2")
    assert laser.get("A1").shape == (10, 10)
    pytest.approx(laser.get("A1").sum(), 100)
    # Calibration
    calibration = laser.calibration["A1"]
    assert calibration.gradient == 1.0
    assert calibration.intercept == 2.0
    assert calibration.rsq is None
    assert calibration.weighting == "x"
    assert np.all(calibration.points == np.array([[1, 1], [2, 2], [3, 3]]))
    assert calibration.unit == "test"
    # Saving
    temp = tempfile.NamedTemporaryFile(suffix=".npz")
    io.npz.save(temp.name, [laser])
    assert filecmp.cmp(temp.name, os.path.join(data_path, "test.npz"))
    temp.close()