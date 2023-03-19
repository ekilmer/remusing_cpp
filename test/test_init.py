import remusing_cpp


def test_version():
    version = getattr(remusing_cpp, "__version__", None)
    assert version is not None
    assert isinstance(version, str)
