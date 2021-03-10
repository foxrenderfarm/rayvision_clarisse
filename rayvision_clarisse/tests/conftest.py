"""The plugin of the pytest.

The pytest plugin hooks do not need to be imported into any test code, it will
load automatically when running pytest.

References:
    https://docs.pytest.org/en/2.7.3/plugins.html

"""

# pylint: disable=import-error
import os
import sys

import pytest

from rayvision_utils.cmd import Cmd


@pytest.fixture()
def user_info():
    """Get user info."""
    return {
        "domain": "task.renderbus.com",
        "platform": "2",
        "access_id": "df6d1d6s3dc56ds6",
        "access_key": "fa5sd565as2fd65",
        "local_os": 'windows',
        "workspace": "c:/workspace",
        "render_software": "Clarisse",
        "software_version": "clarisse_ifx_4.0_sp3",
        "project_name": "Project1",
        "plugin_config": {},
    }


@pytest.fixture()
def cg_file_c(tmpdir):
    """Get render cg file."""
    return {
        'cg_file': str(tmpdir.join('muti_layer_test.project'))
    }


@pytest.fixture()
def handle_cmd():
    """Get a Cmd object."""
    return Cmd()


@pytest.fixture()
def check(task):
    """Create an RayvisionCheck object."""
    from rayvision_api.task.check import RayvisionCheck
    return RayvisionCheck(task)


@pytest.fixture()
def clarisse(tmpdir):
    """Create an Clarisse object."""
    from rayvision_clarisse.analyse_clarisse import AnalyzeClarisse
    if "win" in sys.platform.lower():
        os.environ["USERPROFILE"] = str(tmpdir)
    else:
        os.environ["HOME"] = str(tmpdir)
    return AnalyzeClarisse(str(tmpdir), "clarisse_ifx_4.0_sp3")
