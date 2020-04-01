# -*- coding: utf-8 -*-
"""only analyze clarisse"""

from rayvision_clarisse.analyse_clarisse import AnalyzeClarisse

analyze_info = {
    "cg_file": r"D:\files\CG FILE\clarisse_test1.project",
    "workspace": "c:/workspace",
    "software_version": "clarisse_ifx_4.0_sp3",
    "project_name": "Project1",
    "plugin_config": {}
}

AnalyzeClarisse(**analyze_info).analyse()