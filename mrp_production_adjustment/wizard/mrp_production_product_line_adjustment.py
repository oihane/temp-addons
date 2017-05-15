# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class MrpProductionProductLineAdjustment(models.TransientModel):
    _name = 'mrp.production.product.line.adjustment'

    qty = fields.Float(string='Product QTY', required=True,
                       digits=dp.get_precision('Product Unit of Measure'))

    @api.model
    def default_get(self, var_fields):
        res = super(MrpProductionProductLineAdjustment,
                    self).default_get(var_fields)
        line = self.env['mrp.production.product.line'].browse(
            self.env.context.get('active_id'))
        res.update({'qty': line.product_qty})
        return res

    @api.multi
    def change_qty(self):
        line = self.env['mrp.production.product.line'].browse(
            self.env.context.get('active_id'))
        line.product_qty = self.qty
        for product_line in line.production_id.product_lines.filtered(
                lambda r: r.id != line.id):
            product_line.product_qty = (
                (self.qty / line.bom_line.product_qty) *
                product_line.bom_line.product_qty)
            line.production_id.product_qty = sum(
                line.production_id.mapped('product_lines.product_qty'))
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'mrp.production',
            'res_id': line.production_id.id,
            'type': 'ir.actions.act_window',
        }
