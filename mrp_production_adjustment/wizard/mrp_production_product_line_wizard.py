# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class WizProductionProductLine(models.TransientModel):
    _inherit = 'wiz.production.product.line'

    @api.onchange('product_id')
    def _onchange_check_available_lots(self):
        lots = self.env['stock.production.lot']
        product_lots = self.env['stock.production.lot'].search(
            [('product_id', '=', self.product_id.id)])
        for lot in product_lots:
            if self.env['mrp.production']._check_lot_quantity(
                    lot.id, self.production_id.location_src_id.id, 0.0):
                lots |= lot
        return {'domain': {'lot': [('id', 'in', lots.ids)]}}
