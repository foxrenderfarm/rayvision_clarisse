# -*- coding: utf-8 -*-
"""A interface for clarisse."""

# Import built-in models
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str

import codecs
import json
import logging
import hashlib
import os
import re
import sys
import time

from rayvision_utils import utils
from rayvision_utils import constants
from rayvision_utils.cmd import Cmd
from rayvision_utils.exception import tips_code
from rayvision_utils.exception.exception import AnalyseFailError
from rayvision_clarisse.utils import convert_path
from rayvision_clarisse.utils import str_to_unicode
from rayvision_clarisse.utils import unicode_to_str

VERSION = sys.version_info[0]


class AnalyzeClarisse(object):
    def __init__(self, cg_file, software_version, project_name=None,
                 plugin_config=None, render_software="Clarisse",
                 local_os=None, workspace=None, custom_exe_path=None,
                 platform="2"):
        """Initialize and examine the analysis information.

        Args:
            cg_file (str): Scene file path.
            software_version (str): Software version.
            project_name (str): The project name.
            plugin_config (dict): Plugin information.
            render_software (str): Software name, Maya by default.
            local_os (str): System name, linux or windows.
            workspace (str): Analysis out of the result file storage path.
            custom_exe_path (str): Customize the exe path for the analysis.
            platform (str): Platform no.

        """
        self.logger = logging.getLogger(__name__)

        self.check_path(cg_file)
        self.cg_file = cg_file

        self.render_software = render_software
        self.software_version = software_version
        self.project_name = project_name
        self.plugin_config = plugin_config

        local_os = self.check_local_os(local_os)
        self.local_os = local_os
        self.tmp_mark = str(int(time.time()))
        workspace = os.path.join(self.check_workspace(workspace),
                                 self.tmp_mark)
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        self.workspace = workspace

        if custom_exe_path:
            self.check_path(custom_exe_path)
        self.custom_exe_path = custom_exe_path

        self.platform = platform

        self.task_json = os.path.join(workspace, "task.json")
        self.tips_json = os.path.join(workspace, "tips.json")
        self.asset_json = os.path.join(workspace, "asset.json")
        self.upload_json = os.path.join(workspace, "upload.json")
        self.tips_info = {}
        self.task_info = {}
        self.asset_info = {}
        self.upload_info = {}

        py_version = sys.version_info.major
        if py_version != 2:
            py = "py3"
        else:
            py = "py2"
        self.analyze_script_path = os.path.normpath(os.path.join(
            os.path.dirname(__file__).replace("\\", "/"),
            "tool", py, "Analyze.exe"))

        self.check_path(self.analyze_script_path)
        self.py_version = sys.version_info[0]

    @staticmethod
    def check_path(tmp_path):
        """Check if the path exists."""
        if not os.path.exists(tmp_path):
            raise Exception("{} is not found".format(tmp_path))

    def add_tip(self, code, info):
        """Add error message.

        Args:
            code (str): error code.
            info (str or list): Error message description.

        """
        if isinstance(info, str):
            self.tips_info[code] = [info]
        elif isinstance(info, list):
            self.tips_info[code] = info
        else:
            raise Exception("info must a list or str.")

    def save_tips(self):
        """Write the error message to tips.json."""
        utils.json_save(self.tips_json, self.tips_info, ensure_ascii=False)

    @staticmethod
    def check_local_os(local_os):
        """Check the system name.

        Args:
            local_os (str): System name.

        Returns:
            str

        """
        if not local_os:
            if "win" in sys.platform.lower():
                local_os = "windows"
            else:
                local_os = "linux"
        return local_os

    def check_workspace(self, workspace):
        """Check the working environment.

        Args:
            workspace (str):  Workspace path.

        Returns:
            str: Workspace path.

        """
        if not workspace:
            if self.local_os == "windows":
                workspace = os.path.join(os.environ["USERPROFILE"],
                                         "renderfarm_sdk")
            else:
                workspace = os.path.join(os.environ["HOME"], "renderfarm_sdk")
        else:
            self.check_path(workspace)

        return workspace

    def write_task_json(self):
        """The initialization task.json."""
        constants.TASK_INFO["task_info"]["input_cg_file"] = self.cg_file.replace("\\", "/")
        constants.TASK_INFO["task_info"]["project_name"] = self.project_name
        constants.TASK_INFO["task_info"]["cg_id"] = constants.CG_SETTING.get(self.render_software.capitalize())
        constants.TASK_INFO["task_info"]["os_name"] = "1" if self.local_os == "windows" else "0"
        constants.TASK_INFO["task_info"]["platform"] = self.platform
        constants.TASK_INFO["software_config"] = {
            "plugins": self.plugin_config,
            "cg_version": self.software_version,
            "cg_name": self.render_software
        }
        utils.json_save(self.task_json, constants.TASK_INFO)

    def print_info(self, info):
        """Print info by logger.

        Args:
            info (str): Output information.

        """
        if self.py_version == 3:
            self.logger.info(info)
        else:
            self.logger.info("%s", unicode_to_str(
                info,
                logger=self.logger,
                py_version=self.py_version))

    def print_info_error(self, info):
        """Print error info by logger.

        Args:
            info (str): Output information.

        """
        if self.py_version == 3:
            self.logger.info("[Analyze Error]%s", info)
        else:
            self.logger.info("[Analyze Error]%s", unicode_to_str(
                info,
                logger=self.logger,
                py_version=self.py_version))

    def writing_error_abort(self, error_code, info=None):
        """Collect error abort to tips_info.

        Args:
            error_code (str): Error code.
            info (None, str): Default is None.

        """
        if isinstance(info, list):
            pass
        else:
            info = str_to_unicode(info, py_version=self.py_version)
        if error_code in self.tips_info:
            if isinstance(self.tips_info[error_code], list) and len(
                    self.tips_info[error_code]) > 0 and (
                        self.tips_info[error_code][0] != info):
                error_list = self.tips_info[error_code]
                error_list.append(info)
                self.tips_info[error_code] = error_list
        else:
            if ((self.py_version == 2 and isinstance(info, str)) or (
                    self.py_version == 3 and isinstance(info, str))) and (
                        info != ""):
                ret = re.findall(r"Reference file not found.+?: +(.+)", info,
                                 re.I)
                if ret:
                    self.tips_info["25009"] = [ret[0]]
                else:
                    self.tips_info[error_code] = [info]

            elif isinstance(info, list):
                self.tips_info[error_code] = info
            else:
                self.tips_info[error_code] = []

    def write_tips_info(self):
        """Write tips info."""
        if os.path.exists(self.tips_json):
            with open(self.tips_json, 'r') as tips_f:
                json_src = json.load(tips_f)
                for i in self.tips_info:
                    json_src[i] = self.tips_info[i]
        else:
            json_src = self.tips_info
        with codecs.open(self.tips_json, 'w', 'utf-8') as tips_f:
            json.dump(json_src, tips_f, ensure_ascii=False, indent=4)

    def check_result(self):
        """Check that the analysis results file exists."""
        for json_path in [self.task_json, self.asset_json,
                          self.tips_json]:
            if not os.path.exists(json_path):
                msg = "Json file is not generated: {0}".format(json_path)
                return False, msg
        return True, None

    def analyse_cg_file(self):
        """Start analyse cg file.

        Examples cmd command:
            "D:/myproject/internal_news/rayvision_clarisse/rayvision_clarisse
            /tool/Analyze.exe" -cf
            "E:/copy/DHGB_sc05_zhuta_610-1570_v0102.project" -tj
             "c:/workspace/work/10398483/task.json"

        """
        analyse_cmd = '\"%s\" -cf \"%s\" -tj \"%s\"' % (
            self.analyze_script_path, os.path.normpath(self.cg_file),
            os.path.normpath(self.task_json))
        self.print_info("\n\n-----------------------------"
                        "--------------Start clarisse analyse--------"
                        "-----------------------------\n\n")
        self.print_info("analyse cmd info:\n  ")

        code, _, _ = Cmd.run(analyse_cmd, shell=True)

        if code != 0:
            self.add_tip(tips_code.UNKNOW_ERR, "")
            self.save_tips()
            raise AnalyseFailError

        # Determine whether the analysis is successful by
        #  determining whether a json file is generated.
        status, msg = self.check_result()
        if status is False:
            self.add_tip(tips_code.UNKNOW_ERR, msg)
            self.save_tips()
            raise AnalyseFailError(msg)
        self.logger.info('--[end]--')

    def get_file_md5(self, file_path):
        """Generate the md5 values for the scenario."""
        hash_md5 = hashlib.md5()
        if os.path.exists(file_path):
            with open(file_path, 'rb') as file_path_f:
                while True:
                    data_flow = file_path_f.read(8096)
                    if not data_flow:
                        break
                    hash_md5.update(data_flow)
        return hash_md5.hexdigest()

    def gather_upload_dict(self):
        """Gather upload info.

        Examples:
            {
                "asset": [
                    {
                        "local": "E:/copy/muti_layer_test.ma",
                        "server": "/E/copy/muti_layer_test.ma"
                    }
                ]
        }

        """
        self.upload_info = utils.json_load(self.upload_json)
        self.upload_info["asset"].append({
            "local": self.cg_file.replace("\\", "/"),
            "server": convert_path(self.cg_file)
        })
        self.upload_info["scene"] = [
            {
                "local": self.cg_file.replace("\\", "/"),
                "server": convert_path(self.cg_file),
                "hash": self.get_file_md5(self.cg_file)
            }
        ]
        utils.json_save(self.upload_json, self.upload_info)

    def analyse(self, no_upload=False):
        """Analytical master method for clarrise."""
        self.write_task_json()
        self.analyse_cg_file()

        self.tips_info = utils.json_load(self.tips_json)
        self.asset_info = utils.json_load(self.asset_json)
        self.task_info = utils.json_load(self.task_json)
        if not no_upload:
            self.gather_upload_dict()
        self.logger.info("analyse end.")
