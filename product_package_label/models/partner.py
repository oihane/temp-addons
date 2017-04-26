# -*- coding: utf-8 -*-
# Copyright © 2015-2017 AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('child_ids', 'child_ids.report_ids')
    def _compute_childs_reports(self):
        for partner in self:
            child_report_ids = self.env['product.label.report.copy']
            for child in partner.child_ids:
                child_report_ids |= child.report_ids
            partner.childs_report_ids = [(6, 0, child_report_ids.ids)]

    report_ids = fields.One2many(
        comodel_name='product.label.report.copy',
        inverse_name='partner_id', string='Report')
    childs_report_ids = fields.Many2many(
        comodel_name='product.label.report.copy', string='Reports',
        compute='_compute_childs_reports', relation='rel_partner_report_copy')
