# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class QcTriggerProductionLine(models.Model):
    _inherit = "qc.trigger.line"
    _name = "qc.trigger.mrp_production_line"

    production_id = fields.Many2one(
        comodel_name='mrp.production', string='Manufacturing Order')
    trigger = fields.Many2one(
        default=lambda self: self.env.ref(
            'quality_control_mrp.qc_trigger_mrp'))

    def get_trigger_line_for_product(
            self, trigger, product, partner=False, production=False):
        trigger_lines = super(
            QcTriggerProductionLine,
            self).get_trigger_line_for_product(
                trigger, product, partner=partner)
        for trigger_line in production.qc_triggers:
            trigger_lines.add(trigger_line)
        return trigger_lines
