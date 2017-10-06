# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP Production Adjustments",
    "version": "8.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
    ],
    "depends": [
        "mrp_production_add_middle_stuff_lot",
        "quality_control_mrp",
        "web_dialog_size",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mrp_production_adjustment_data.xml",
        "wizard/mrp_production_adjustment_line_wizard_view.xml",
        "wizard/mrp_production_adjustment_inspection_wizard_view.xml",
        "wizard/mrp_production_adjustment_history_view.xml",
        "views/mrp_production_view.xml",
        "views/qc_test_view.xml",
    ],
    "installable": True,
}
