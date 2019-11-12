# -*- coding: utf-8 -*-
"""Clarisse  analyzes documents."""

from builtins import str
import os
import sys
import logging
import codecs
import json
import re
import platform

from rayvision_utils import utils
from rayvision_utils.exception import tips_code
from rayvision_utils.exception.exception import AnalyseFailError
from rayvision_utils.json_handle import JsonHandle

from rayvision_clarisse.utils import convert_path
from rayvision_clarisse.utils import str_to_unicode
from rayvision_clarisse.utils import unicode_to_str

CLIENT_SCRIPT = os.path.abspath(sys.path[0] + '/../submit/')
sys.path.append(CLIENT_SCRIPT)


class Clarisse(JsonHandle):
    """Inherit JsonHandle.

    Mainly responsible for the processing before and after analysis.

    """

    def __init__(self, *args, **kwargs):
        """Instantiate Clarisse interface."""
        super(Clarisse, self).__init__(*args, **kwargs)
        self.exe_name = "Analyze.exe"
        self.py_version = sys.version_info[0]
        self.tips_info_dict = {}
        self.asset_info_dict = {}
        self.task_info_dict = self.task.task_info
        self.user_id = self.task.task_info["task_info"]["user_id"]
        self.logger = logging.getLogger(__name__)
        if not os.path.exists(self.cg_file):
            self.writing_error_abort("40001", self.cg_file)
            self.logger.info("%s is not exists.......", self.cg_file)

        self.cg_version = self.task.task_info['software_config']['cg_version']

        self.analyze_flag_file = self.task.work_dir + "/" + "analyze_sucess"

        self.current_os = platform.system().lower()
        analyze_script = os.path.dirname(__file__)
        self.analyze_script_path = os.path.normpath(os.path.join(
            analyze_script.replace("\\", "/"), "tool", "Analyze.exe"))
        if not os.path.exists(self.analyze_script_path):
            self.writing_error_abort("40002")

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
        """Collect error abort to tips_info_dict.

        Args:
            error_code (str): Error code.
            info (None, str): Default is None.

        """
        if isinstance(info, list):
            pass
        else:
            info = str_to_unicode(info, py_version=self.py_version)
        if error_code in self.tips_info_dict:
            if isinstance(self.tips_info_dict[error_code], list) and len(
                    self.tips_info_dict[error_code]) > 0 and (
                        self.tips_info_dict[error_code][0] != info):
                error_list = self.tips_info_dict[error_code]
                error_list.append(info)
                self.tips_info_dict[error_code] = error_list
        else:
            if ((self.py_version == 2 and isinstance(info, str)) or (
                    self.py_version == 3 and isinstance(info, str))) and (
                        info != ""):
                ret = re.findall(r"Reference file not found.+?: +(.+)", info,
                                 re.I)
                if ret:
                    self.tips_info_dict["25009"] = [ret[0]]
                else:
                    self.tips_info_dict[error_code] = [info]

            elif isinstance(info, list):
                self.tips_info_dict[error_code] = info
            else:
                self.tips_info_dict[error_code] = []

    def write_tips_info(self):
        """Write tips info."""
        if os.path.exists(self.tips_json):
            with open(self.tips_json, 'r') as tips_f:
                json_src = json.load(tips_f)
                for i in self.tips_info_dict:
                    json_src[i] = self.tips_info_dict[i]
        else:
            json_src = self.tips_info_dict
        with codecs.open(self.tips_json, 'w', 'utf-8') as tips_f:
            json.dump(json_src, tips_f, ensure_ascii=False, indent=4)

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
            os.path.normpath(self.task.task_json_path))
        self.print_info("\n\n-----------------------------"
                        "--------------Start clarisse analyse--------"
                        "-----------------------------\n\n")
        self.print_info("analyse cmd info:\n  ")

        code, _, _ = self.cmd.run(analyse_cmd, shell=True)

        if code != 0:
            self.tips.add(tips_code.UNKNOW_ERR)
            self.tips.save_tips()
            raise AnalyseFailError

        # Determine whether the analysis is successful by
        #  determining whether a json file is generated.
        status, msg = self.json_exist()
        if status is False:
            self.tips.add(tips_code.UNKNOW_ERR, msg)
            self.tips.save_tips()
            raise AnalyseFailError(msg)
        self.logger.info('--[end]--')

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
        self.task.upload_info = utils.json_load(self.task.upload_json_path)
        self.task.upload_info["asset"].append({
            "local": self.cg_file,
            "server": convert_path(self.cg_file)
        })

    def run(self):
        """Analytical master method for clarrise."""
        self.dump_task_json()
        self.analyse_cg_file()
        self.gather_upload_dict()
        self.load_output_json()
        self.write_cg_path()
        self.logger.info("analyse end.")
