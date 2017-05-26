# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Sale packaging",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "Sales Management",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "depends": [
        "sale",
        "mrp_packaging",
    ],
    "data": [
        "data/sale_mrp_packaging_data.xml",
        "data/sale_mrp_packaging_data.yml",
        "views/procurement_view.xml",
    ],
    "installable": True,
}
