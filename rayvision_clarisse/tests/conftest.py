"""The plugin of the pytest.

The pytest plugin hooks do not need to be imported into any test code, it will
load automatically when running pytest.

References:
    https://docs.pytest.org/en/2.7.3/plugins.html

"""


# pylint: disable=import-error
import pytest
from rayvision_api.task.handle import RayvisionTask
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
def task(user_info, cg_file_c, mocker):
    """Create an RayvisionTask object."""
    mocker_task_id = mocker.patch.object(RayvisionTask, 'get_task_id')
    mocker_task_id.return_value = '1234567'
    mocker_user_id = mocker.patch.object(RayvisionTask, 'get_user_id')
    mocker_user_id.return_value = '10000012'
    mocker_user_id = mocker.patch.object(RayvisionTask,
                                         'check_and_add_project_name')
    mocker_user_id.return_value = '147258'
    return RayvisionTask(cg_file=cg_file_c['cg_file'], **user_info)


@pytest.fixture()
def check(task):
    """Create an RayvisionCheck object."""
    from rayvision_api.task.check import RayvisionCheck
    return RayvisionCheck(task)


@pytest.fixture()
def clarisse(cg_file_c, task):
    """Create an Clarisse object."""
    from rayvision_clarisse.analyse_clarisse import Clarisse
    return Clarisse(str(cg_file_c['cg_file']), task, 2013, '')
