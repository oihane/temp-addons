# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, exceptions, fields, models, _
from openerp.addons import decimal_precision as dp


class MrpProductionAdjustmentLine(models.Model):
    _name = 'mrp.production.adjustment.line'
    _order = 'production_id, addition_order'

    production_id = fields.Many2one(
        comodel_name='mrp.production', string='Manufacturing Order',
        required=True, ondelete='cascade')
    addition_order = fields.Char(string='Addition Order', required=True)
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product')
    product_qty = fields.Float(
        string='Quantity', digits=dp.get_precision('Product Unit of Measure'))
    product_uom_id = fields.Many2one(
        comodel_name='product.uom', string='Unit of Measure')
    move_id = fields.Many2one(
        comodel_name='stock.move', string='Consume move')
    move_state = fields.Selection(
        string='Move state', related='move_id.state')
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot', string='Reserved Lot',
        domain="[('product_id', '=', product_id)]")
    ph_before = fields.Float(string='ph (before addition)')
    ph_after = fields.Float(string='ph (after addition)')
    visco_before = fields.Integer(string='Viscosity (before addition)')
    visco_after = fields.Integer(string='Viscosity (after addition)')
    thixo_before = fields.Float(string='Thixotropy (before addition)')
    thixo_after = fields.Float(string='Thixotropy (after addition)')
    inspection_id = fields.Many2one(
        comodel_name='qc.inspection', string='Lab Inspection',
        domain="[('production', '=', production_id)]")
    inspection_state = fields.Selection(related='inspection_id.state')

    _sql_constraints = [
        ('ph_before', ' CHECK (ph_before >= 0 and ph_before <= 14)',
         'Wrong pH value!'),
        ('ph_after', ' CHECK (ph_after >= 0 and ph_after <= 14)',
         'Wrong pH value!'),
    ]

    @api.constrains('addition_order')
    def _constraint_addition_order(self):
        if (not self.addition_order.isdigit() and
                not self.addition_order == 'FINAL'):
            raise exceptions.ValidationError(
                _("Please review adjustment lines. Addition order must be an"
                  " integer or 'FINAL'"))
        if len(self.filtered(
                lambda x: x.production_id == self.production_id and
                x.addition_order == 'FINAL')) > 1:
            raise exceptions.ValidationError(
                _("Please review adjustment lines. Only one 'FINAL' line is"
                  "allowed"))

    @api.model
    def create(self, values):
        production = self.env['mrp.production'].browse(
            values.get('production_id'))
        if self.env.context.get('final_addition', False):
            values['addition_order'] = 'FINAL'
    #         # añadir valores de los campos 'visco' 'tixo' y 'ph_lab' al lote
    #         lots = (
    #             (production.mapped('move_created_ids.restrict_lot_id') |
    #              production.mapped('move_created_ids2.restrict_lot_id')) |
    #             (production.mapped(
    #                 'expected_production.move_created_ids.restrict_lot_id') |
    #              production.mapped(
    #                 'expected_production.move_created_ids2.restrict_lot_id')))
    #         lots.write({
    #             'viscosity': values.get('viscosity'),
    #             'thixotropy': values.get('tixotrophy'),
    #             'ph': values.get('ph_lab'),
    #         })
        if 'addition_order' not in values:
            values['addition_order'] = len(production.adjustment_ids) + 1
        return super(MrpProductionAdjustmentLine, self).create(values)

    # @api.multi
    # def write(self, values):
    #     if values.get('product_id') or values.get('product_qty') or\
    #             values.get('lot_id'):
    #         for move in self.mapped('move_id'):
    #             if move.state in ('draft', 'confirmed', 'assigned'):
    #                 if move.state == 'assigned':
    #                     move.do_unreserve()
    #                 move.write({
    #                     'product_id': values.get('product_id',
    #                                              self.product_id.id),
    #                     'product_uom_qty': values.get('product_qty',
    #                                                   self.product_qty),
    #                     'restrict_lot_id': values.get('lot_id',
    #                                                   self.lot_id.id)
    #                 })
    #                 if move.raw_material_production_id.state and\
    #                         move.raw_material_production_id.state not in\
    #                         ('confirmed', 'draft'):
    #                     move.action_assign()
    #         if not self.mapped('move_id'):
    #             product_wizard = self.env[
    #                 'wiz.production.product.line'].create({
    #                     'production_id': values.get('production_id',
    #                                                 self.production_id.id),
    #                     'product_id': values.get('product_id',
    #                                              self.product_id.id),
    #                     'product_qty': values.get('product_qty',
    #                                               self.product_qty),
    #                     'lot': values.get('lot_id', self.lot_id.id),
    #                 })
    #             move = product_wizard.add_product()
    #             values.update({'move_id': move.id})
    #     elif not values.get('product_id', True):
    #         self.mapped('move_id').action_cancel()
    #     if ((values.get('addition_order') == 'OFICIAL' or
    #             self.addition_order == 'OFICIAL') and
    #             (values.get('viscosity') or values.get('tixotrophy') or
    #              values.get('ph_lab'))):
    #         lots = self.production_id.move_created_ids2.filtered(
    #             lambda x: x.product_id == self.production_id.product_id
    #             ).mapped('lot_ids')
    #         for expected in self.mapped(
    #                 'production_id.expected_production').filtered(
    #                     lambda x: x.state != 'cancel'):
    #             lots |= expected.move_created_ids.filtered(
    #                 lambda x: x.product_id == expected.product_id
    #                 ).mapped('lot_ids')
    #             lots |= expected.move_created_ids2.filtered(
    #                 lambda x: x.product_id == expected.product_id
    #                 ).mapped('lot_ids')
    #         lots.write({
    #             'viscosity': values.get('viscosity') or self.viscosity,
    #             'thixotropy': values.get('tixotrophy') or self.tixotrophy,
    #             'ph': values.get('ph_lab') or self.ph_lab,
    #         })
    #     return super(MrpProductionAdjustmentLine, self).write(values)

    @api.multi
    def unlink(self):
        for line in self:
            if line.move_id.state == 'done':
                line.move_id = False
            elif line.move_id.state != 'draft':
                line.move_id.action_cancel()
            return super(MrpProductionAdjustmentLine, line).unlink()

    @api.multi
    def button_set_lab_test(self):
        action = self.env.ref(
            'mrp_production_adjustment.set_adjustment_test_action')
        action = action.read()[0]
        action['context'].update({
            'active_id': self.id,
            'active_ids': self.ids,
            'active_model': self._model._name,
        })
        return action


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    adjustment_ids = fields.One2many(
        comodel_name='mrp.production.adjustment.line',
        inverse_name='production_id', string='Adjustment Lines')
