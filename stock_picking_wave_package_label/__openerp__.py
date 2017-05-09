# -*- coding: utf-8 -*-
# Copyright © 2015-2017 AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Stock Picking Wave Package Label",
    "version": "8.0.1.0.0",
    "category": "Inventory, Logistic, Storage",
    "license": "AGPL-3",
    "author": "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
    ],
    "depends": [
        "product_package_label",
        "stock_picking_wave_management",
        "base_report_to_printer",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_wave_view.xml",
        "views/report_xml_view.xml",
    ],
    "installable": True,
}
