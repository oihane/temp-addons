# -*- coding: utf-8 -*-
# Copyright © 2015-2017 AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Package Label",
    "version": "8.0.3.0.0",
    "category": "Hidden/Dependency",
    "license": "AGPL-3",
    "author": "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Ainara Galdona <ainaragaldona@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "depends": [
        "base",
        "product_packaging_views",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_view.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
}
