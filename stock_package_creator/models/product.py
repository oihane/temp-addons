# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class ProductUl(models.Model):
    _inherit = 'product.ul'

    @api.multi
    def create_quant_pck_from_ul(self):
        self.ensure_one()
        vals = {
            'ul_id': self.id,
            'height': self.height,
            'width': self.width,
            'length': self.length,
            'empty_weight': self.weight,
        }
        return self.env['stock.quant.package'].create(vals)


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    ul_id = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit',
        domain="[('type','=','pallet')]")
