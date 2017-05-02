# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    pack = fields.Boolean(
        default=False,
        help='If this field is marked, when transferring it will automatically'
        ' pack the material.')
