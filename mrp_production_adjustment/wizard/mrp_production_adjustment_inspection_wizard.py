# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class MrpProductionAdjustmentInspectionWizard(models.TransientModel):
    _name = 'mrp.production.adjustment.inspection.wizard'

    adjustment_id = fields.Many2one(
        comodel_name='mrp.production.adjustment.line',
        string='Adjustment Line', required=True,
        default=lambda self: self.env.context.get('active_id', False))
    test_id = fields.Many2one(
        comodel_name='qc.test', string='Test', required=True,
        domain="[('adjustment_test','=',True)]")

    @api.multi
    def button_set_lab_test(self):
        trigger_line = self.env['qc.trigger.mrp_production_line'].create({
            'production_id': self.adjustment_id.production_id.id,
            'test': self.test_id.id,
        })
        move = self.adjustment_id.production_id.move_created_ids[:1] or \
            self.adjustment_id.production_id.move_created_ids2.filtered(
            lambda r: r.state == 'done')[:1]
        self.adjustment_id.inspection_id = self.env[
            'qc.inspection']._make_inspection(move, trigger_line)
        trigger_line.unlink()
