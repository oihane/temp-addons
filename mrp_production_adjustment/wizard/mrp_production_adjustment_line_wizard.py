# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, exceptions, fields, models, _
from openerp.addons import decimal_precision as dp


class MrpProductionAdjustmentLineWizard(models.TransientModel):
    _name = 'mrp.production.adjustment.line.wizard'

    production_id = fields.Many2one(
        comodel_name='mrp.production', string='Manufacturing Order',
        select=True,
        default=lambda self: self.env.context.get('active_id'))
    # addition_product_filter = fields.Boolean(default=True)
    # temperature = fields.Float()
    # ph = fields.Float()
    # watts = fields.Float()
    ph_before = fields.Float(string='ph (before addition)')
    ph_after = fields.Float(string='ph (after addition)')
    visco_before = fields.Integer(string='Viscosity (before addition)')
    visco_after = fields.Integer(string='Viscosity (after addition)')
    thixo_before = fields.Float(string='Thixotropy (before addition)')
    thixo_after = fields.Float(string='Thixotropy (after addition)')
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product')
    product_qty = fields.Float(
        string='Quantity', digits=dp.get_precision('Product Unit of Measure'))
    product_uom_id = fields.Many2one(
        comodel_name='product.uom', string='Unit of Measure')
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot', string='Reserved Lot',
        domain="[('product_id', '=', product_id)]")
    final_addition = fields.Boolean()

    _sql_constraints = [
        ('ph_before', ' CHECK (ph_before >= 0 and ph_before <= 14)',
         'Wrong pH value!'),
        ('ph_after', ' CHECK (ph_after >= 0 and ph_after <= 14)',
         'Wrong pH value!'),
    ]

    # @api.multi
    # @api.onchange('addition_product_filter')
    # def onchange_addition_product_filter(self):
    #     self.ensure_one()
    #     domain = []
    #     active_model = self.env.context.get('active_model')
    #     if self.addition_product_filter and active_model == 'mrp.production':
    #         production = self.env[active_model].browse(
    #             self.env.context.get('active_id'))
    #         products = production.bom_id.mapped(
    #             'adjustment_product_ids')
    #         domain = [('id', 'in', products.ids)]
    #     return {'domain': {'product_id': domain}}

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id
        self.product_qty = 1.0 if not self.product_qty and self.product_id \
            else self.product_qty

    @api.constrains('product_id', 'product_uom_id')
    def _check_product_uom_id(self):
        for record in self.filtered(
                lambda r: r.product_id and r.product_uom_id):
            if record.product_id.uom_id.category_id != \
                    record.product_uom_id.category_id:
                raise exceptions.ValidationError(
                    _('Please use an UoM in the same UoM category.'))

    @api.constrains('product_id', 'product_qty')
    def _check_product_qty(self):
        for record in self.filtered(lambda r: r.product_id):
            if record.product_qty <= 0:
                raise exceptions.ValidationError(
                    _('Please provide a positive quantity to add'))

    @api.multi
    def make_adjustment(self):
        move = self.env['stock.move']
        if self.product_id and self.product_qty:
            product_wizard = self.env['wiz.production.product.line'].create({
                'production_id': self.production_id.id,
                'product_id': self.product_id.id,
                'product_qty': self.product_qty,
                'product_uom_id': self.product_uom_id.id,
                'lot': self.lot_id.id,
            })
            move = product_wizard.add_product()
        res = self.with_context(final_addition=self.final_addition).env[
            'mrp.production.adjustment.line'].create({
                'production_id': self.production_id.id,
                'product_id': self.product_id.id,
                'product_qty': self.product_qty,
                'product_uom_id': self.product_uom_id.id,
                'lot_id': self.lot_id.id,
                'ph_before': self.ph_before,
                'ph_after': self.ph_after,
                'visco_before': self.visco_before,
                'visco_after': self.visco_after,
                'thixo_before': self.thixo_before,
                'thixo_after': self.thixo_after,
                # 'temperature': self.temperature,
                # 'ph': self.ph,
                # 'watts': self.watts,
                # 'viscosity': self.viscosity,
                # 'tixotrophy': self.tixotrophy,
                # 'ph_lab': self.ph_lab,
                'move_id': move.id,
            })
        return res
