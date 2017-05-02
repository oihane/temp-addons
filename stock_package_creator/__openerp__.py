# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Stock package creator",
    "summary": "A.K.A. as palletizer",
    "version": "8.0.1.0.0",
    "category": "Inventory, Logistic, Storage",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
    ],
    "depends": [
        "stock",
        "stock_picking_package_info",
        "product_packaging_through_attributes",
        "web_context_tunnel",
    ],
    "data": [
        "views/product_view.xml",
        "views/stock_view.xml",
        "wizard/stock_transfer_details_view.xml",
    ],
    "installable": True,
}
