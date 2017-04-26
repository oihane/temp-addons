# -*- coding: utf-8 -*-
# Copyright © 2015-2017 AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import _, api, exceptions, fields, models


class ProductLabelReportCopy(models.Model):
    _name = 'product.label.report.copy'
    _rec_name = 'report_id'

    report_id = fields.Many2one(
        comodel_name='ir.actions.report.xml', string='Report',
        required=True, ondelete='cascade')
    report_model = fields.Char(
        string='Report Model', related='report_id.model', store=True)
    copy_num = fields.Integer(string='# Copies', default=1)
    supplierinfo_id = fields.Many2one(
        comodel_name='product.supplierinfo', string='Supplierinfo',
        ondelete='cascade')
    product_ul_id = fields.Many2one(
        comodel_name='product.ul', string='Product UL',
        ondelete='cascade')
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Partner',
        ondelete='cascade')
    label_model = fields.Selection(
        selection=[('cube', 'Cube'), ('palet', 'No Numbered Pallet'),
                   ('num_palet', 'Numbered Pallet')],
        string='Label model',
        default=lambda self: self.env.context.get('label_model'))

    @api.constrains('supplierinfo_id', 'product_ul_id', 'partner_id')
    def _check_origin_object(self):
        for record in self:
            if (record.supplierinfo_id and (record.product_ul_id or
                                            record.partner_id)) or\
                    (record.product_ul_id and record.partner_id):
                raise exceptions.ValidationError(
                    _('You must select only one.'))
            if not record.supplierinfo_id and not \
                    record.product_ul_id and not record.partner_id:
                raise exceptions.ValidationError(
                    _('You must select at least one Supplierinfo '
                      'or Product UL or Partner.'))


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    report_ids = fields.One2many(
        comodel_name='product.label.report.copy',
        inverse_name='supplierinfo_id', string='Report')


class ProductUl(models.Model):
    _inherit = 'product.ul'

    report_ids = fields.One2many(
        comodel_name='product.label.report.copy',
        inverse_name='product_ul_id', string='Report')
