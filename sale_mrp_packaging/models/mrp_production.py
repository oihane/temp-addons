# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class PackagingOperation(models.Model):
    _inherit = 'packaging.operation'

    move_prod_id = fields.Many2one(
        comodel_name='stock.move', string='Product Move', readonly=True,
        copy=False)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def create_mo_from_packaging_operation(self):
        for production in self:
            super(MrpProduction,
                  production).create_mo_from_packaging_operation()
