# -*- coding: utf-8 -*-
# Copyright © 2015-2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class MrpProductionAdjustmentHistory(models.TransientModel):
    _name = 'mrp.production.adjustment.history'

    production_min_visco = fields.Integer(string='Min. Viscosity')
    production_max_visco = fields.Integer(string='Max. Viscosity')
    line_ids = fields.One2many(
        comodel_name='mrp.production.adjustment.history.line',
        inverse_name='history_id')
    historicized_moves = fields.Many2many(
        comodel_name='stock.move', relation='production_move_history')

    @api.model
    def default_get(self, field_list):
        res = super(MrpProductionAdjustmentHistory,
                    self).default_get(field_list)
        production_obj = self.env['mrp.production']
        active_production = production_obj.browse(
            self.env.context.get('active_id'))
        productions = production_obj.search(
            [('id', '!=', active_production.id),
             ('product_id', '=', active_production.product_id.id),
             ('bom_id', '=', active_production.bom_id.id),
             ('routing_id', '=', active_production.routing_id.id),
             ('state', 'not in', ('draft', 'cancel'))],
            limit=6, order='date_planned DESC')
        # historicized_products = active_production.bom_id.bom_line_ids.
        # filtered('history').mapped('product_id')
        historicized_products = active_production.bom_id.bom_line_ids.mapped(
            'product_id')
        historicized_moves = active_production.mapped('move_lines').filtered(
            lambda r: r.product_id in historicized_products).sorted(
            lambda m: m.raw_material_production_id.create_date)
        historicized_moves += active_production.mapped('move_lines2').filtered(
            lambda r: r.product_id in historicized_products).sorted(
            lambda m: m.raw_material_production_id.create_date)
        res.update({
            # 'production_min_visco': active_production.min_visco,
            # 'production_max_visco': active_production.max_visco,
            'historicized_moves': [(6, 0, historicized_moves.ids)]})
        used_lots = historicized_moves.mapped('reserved_quant_ids.lot_id') +\
            historicized_moves.mapped('quant_ids.lot_id')
        lines = []
        for production in productions:
            production_data = {
                'production_id': production.id,
                'production_date_planned': production.date_planned,
                'production_product_id': production.product_id.id,
                'production_product_qty': production.product_qty,
                'production_product_uom_id': production.product_uom.id,
                # 'production_min_visco': production.min_visco,
                # 'production_max_visco': production.max_visco,
            }
            moves = production.mapped('move_lines2').filtered(
                lambda r: r.product_id in historicized_products).sorted(
                lambda m: m.raw_material_production_id.create_date)
            for move in moves:
                new_line = {
                    'move_product_id': move.product_id.id,
                    'move_restrict_lot_id': move.restrict_lot_id.id,
                    'move_product_qty': move.product_qty,
                    'move_product_uom_id': move.product_uom.id,
                    'same_lot': move.restrict_lot_id in used_lots,
                }
                new_line.update(production_data)
                lines += [(0, 0, new_line)]
            adjustments = production.mapped('adjustment_ids').sorted(
                lambda a: (a.production_id.create_date, a.addition_order))
            for adjustment in adjustments:
                new_line = {
                    'adj_addition_order': adjustment.addition_order,
                    'adj_product_id': adjustment.product_id.id,
                    'adj_product_qty': adjustment.product_qty,
                    # 'adj_temperature': adjustment.temperature,
                    # 'adj_ph': adjustment.ph,
                    # 'adj_watts': adjustment.watts,
                    # 'adj_viscosity': adjustment.viscosity,
                    # 'adj_tixotrophy': adjustment.tixotrophy,
                    # 'adj_ph_lab': adjustment.ph_lab,
                }
                new_line.update(production_data)
                lines += [(0, 0, new_line)]
        res.update({'line_ids': lines})
        return res


class MrpProductionAdjustmentHistoryLine(models.TransientModel):
    _name = 'mrp.production.adjustment.history.line'

    history_id = fields.Many2one(
        comodel_name='mrp.production.adjustment.history', required='True')
    production_id = fields.Many2one(
        comodel_name='mrp.production', string='Manufacturing Order')
    production_date_planned = fields.Datetime(string='Date Planned')
    production_product_id = fields.Many2one(
        comodel_name='product.product', string='Product')
    production_product_qty = fields.Float(
        string='Qty', digits=dp.get_precision('Product Unit of Measure'))
    production_product_uom_id = fields.Many2one(
        comodel_name='product.uom', string='Product UoM')
    move_product_id = fields.Many2one(
        comodel_name='product.product', string='Consumed Product')
    move_product_uom_id = fields.Many2one(
        comodel_name='product.uom', string='Consumed Product UoM')
    move_restrict_lot_id = fields.Many2one(
        comodel_name='stock.production.lot', string='Consumed Lot')
    move_product_qty = fields.Float(
        string='Consumed Qty',
        digits=dp.get_precision('Product Unit of Measure'))
    same_lot = fields.Boolean(string='Same lots as in OF')
    adj_addition_order = fields.Char(string='Addition Order')
    adj_product_id = fields.Many2one(
        comodel_name='product.product', string='Adjustment Product')
    adj_product_qty = fields.Float(
        string='Quantity', digits=dp.get_precision('Product Unit of Measure'))
    adj_product_uom_id = fields.Many2one(
        comodel_name='product.uom', string='Adjustment Product UoM')
    # adj_temperature = fields.Integer()
    # adj_ph = fields.Float()
    # adj_watts = fields.Integer()
    # adj_viscosity = fields.Integer()
    # adj_tixotrophy = fields.Float()
    # adj_ph_lab = fields.Float()
