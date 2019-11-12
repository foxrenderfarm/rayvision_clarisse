"""Test rayvision_clarisse.analyse_clarisse model."""


def test_print_info(clarisse):
    """Test print_info this interface."""
    info = "test print info"
    assert bool(clarisse.print_info(info)) is False
