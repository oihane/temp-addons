# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.multi
    def do_produce(self):
        production_id = self.env.context.get('active_id', False)
        production = self.env['mrp.production'].browse(production_id)
        lot = (production.mapped('product_lines.lot')[:1]
               if production.production
               else self.env['stock.production.lot'])
        adjustment_line = production.adjustment_ids.filtered(
            lambda x: x.addition_order == 'OFICIAL')
        visco = adjustment_line.viscosity or lot.viscosity
        tixo = adjustment_line.tixotrophy or lot.thixotropy
        ph = adjustment_line.ph_lab or lot.ph
        return super(MrpProductProduce,
                     self.with_context(viscosity=visco, thixotropy=tixo, ph=ph)
                     ).do_produce()
