# -*- coding: utf-8 -*-
# Copyright © 2015-2017 AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class ProductLabelReportCopy(models.Model):
    _inherit = 'product.label.report.copy'

    label_model = fields.Selection(selection_add=[('wave', 'Picking Wave')])


class PickingWavePrintReport(models.Model):
    _name = 'picking.wave.print.report'

    wave_id = fields.Many2one(
        comodel_name='stock.picking.wave', string='Picking Wave',
        ondelete='cascade', required=True)
    report_id = fields.Many2one(
        comodel_name='ir.actions.report.xml', string='Report',
        required=True, ondelete='cascade')
    number_copy = fields.Integer(string='# Copies')
    action_print = fields.Many2one(
        comodel_name='printing.action',
        string='Action', related='report_id.property_printing_action')
    do_print = fields.Boolean(
        string='Print', help='If this check is marked, it will be printed.',
        default=True)

    @api.multi
    def print_reports(self):
        self.ensure_one()
        return self.print_copies(self.wave_id, self.number_copy)

    @api.multi
    def print_copies(self, object, copy_number=0):
        self.ensure_one()
        if not copy_number:
            return {}
        ids_to_print = []
        for x in range(int(copy_number)):
            ids_to_print.append(object.id)
        datas = {'ids': ids_to_print, 'model': self.report_id.model}
        res = self.report_id.print_action_for_report_name(
            self.report_id.report_name)
        if res.get('action') == 'server':
            self.pool['report'].get_pdf(
                self.env.cr, self.env.uid, ids_to_print,
                self.report_id.report_name, html=None, data=None,
                context=self.env.context)
            return {}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': self.report_id.report_name,
            'datas': datas,
        }


class PickingWavePrintLabelPackNumberLine(models.Model):
    _name = 'picking.wave.print.label.pack.number'
    _inherit = 'picking.wave.print.report'

    package_id = fields.Many2one(
        comodel_name='stock.quant.package', string='Package')
    product_ul_id = fields.Many2one(
        comodel_name='product.ul', string='Product Ul')
    packages_number = fields.Float(string='# Pallets')

    @api.multi
    def print_reports(self):
        self.ensure_one()
        return self.print_copies(self.wave_id,
                                 self.number_copy * self.packages_number)


class PickingWavePrintLabelPackNonumber(models.Model):
    _name = 'picking.wave.print.label.pack.nonumber'
    _inherit = 'picking.wave.print.report'

    product_ul_id = fields.Many2one(
        comodel_name='product.ul', string='Product Ul')
    packages_number = fields.Float(string='# Pallets')

    @api.multi
    def print_reports(self):
        self.ensure_one()
        return self.print_copies(self.wave_id,
                                 self.number_copy * self.packages_number)


class StockPickingWave(models.Model):
    _inherit = 'stock.picking.wave'

    report_print = fields.One2many(
        comodel_name='picking.wave.print.report', inverse_name='wave_id',
        string='Reports')
    number_pallet_label_prints = fields.One2many(
        comodel_name='picking.wave.print.label.pack.number',
        inverse_name='wave_id', string='By Pallet Numbers')
    nonumber_pallet_label_prints = fields.One2many(
        comodel_name='picking.wave.print.label.pack.nonumber',
        inverse_name='wave_id', string='By Logistic Unit')

    @api.one
    def button_load_printing_info(self):
        self.number_pallet_label_prints.unlink()
        self.nonumber_pallet_label_prints.unlink()
        self.report_print.unlink()
        for picking in self.picking_ids.filtered(
                lambda p: not p.pack_operation_ids):
            picking.do_prepare_partial()
        by_palet_number = {}
        by_palet_no_number = {}
        pack_line_list = []
        no_pack_line_list = []
        report_print_list = []
        partners = self.partner | self.partner.commercial_partner_id
        reports = partners.mapped('report_ids')
        palet_reports = reports.filtered(
            lambda r: r.label_model in ['palet', 'num_palet'] and
            r.report_model == 'stock.picking.wave')
        wave_reports = reports.filtered(
            lambda r: r.label_model == 'wave' and
            r.report_model == 'stock.picking.wave')
        for operation in self.mapped('picking_ids.pack_operation_ids'):
            by_palet_number, by_palet_no_number = (
                self._calc_by_palet(
                    operation, by_palet_number, by_palet_no_number))
        if by_palet_number:
            pack_line_list = self._charge_by_palet_number(
                self, by_palet_number, palet_reports, pack_line_list)
        if by_palet_no_number:
            no_pack_line_list = self._charge_by_palet_no_number(
                self, by_palet_no_number, palet_reports, no_pack_line_list)
        for print_report in wave_reports:
            wave_print = self.report_print.create({
                'wave_id': self.id,
                'report_id': print_report.report_id.id,
                'number_copy': print_report.copy_num,
            })
            report_print_list.append(wave_print.id)
        self.report_print = report_print_list
        self.number_pallet_label_prints = pack_line_list
        self.nonumber_pallet_label_prints = no_pack_line_list

    def _calc_by_palet(self, operation, by_palet_number, by_palet_no_number):
        result_package = operation.result_package_id
        if not result_package:
            return by_palet_number, by_palet_no_number
        found = False
        for data in by_palet_number:
            datos_array = by_palet_number[data]
            package = datos_array['package']
            operation_ids = datos_array['operation_ids']
            if ((result_package and result_package.id == package.id) or
                    (not result_package and not package)):
                found = True
                operation_ids.append(operation.id)
                my_vals = {
                    'operation_ids': operation_ids,
                }
                by_palet_number[data].update(my_vals)
                break
        if not found:
            my_vals = {
                'package': result_package or False,
                'ul': result_package.ul_id,
                'operation_ids': [operation.id],
            }
            by_palet_number[(result_package.id or False)] = my_vals
            found2 = False
            for data in by_palet_no_number:
                datos_array = by_palet_no_number[data]
                ul = datos_array['ul']
                qty = datos_array['qty']
                operation_ids = datos_array['operation_ids']
                if ((result_package.ul_id and result_package.ul_id.id ==
                     ul.id) or (not result_package.ul_id and not ul)):
                    found2 = True
                    qty += 1
                    operation_ids.append(operation.id)
                    my_vals = {
                        'operation_ids': operation_ids,
                        'qty': qty
                    }
                    by_palet_no_number[data].update(my_vals)
                    break
            if not found2:
                my_vals = {
                    'ul': result_package.ul_id,
                    'qty': 1,
                    'operation_ids': [operation.id],
                }
                by_palet_no_number[(result_package.ul_id or False)] = my_vals
        return by_palet_number, by_palet_no_number

    def _charge_by_palet_number(
            self, wave, by_palet_number, reports, pack_line_list):
        wiz_line_obj = self.env['picking.wave.print.label.pack.number']
        for data in by_palet_number:
            datos_array = by_palet_number[data]
            package = datos_array['package']
            ul = datos_array['ul']
            for report in reports.filtered(
                    lambda r: r.label_model == 'num_palet'):
                line_dict = {
                    'package_id': package and package.id,
                    'product_ul_id': ul.id,
                    'report_id': report.report_id.id,
                    'packages_number': 1,
                    'number_copy': report.copy_num,
                    'wave_id': wave.id
                }
                line_id = wiz_line_obj.create(line_dict)
                pack_line_list.append(line_id.id)
            if not ul:
                continue
            for report in ul.report_ids.filtered(
                    lambda r: r.label_model == 'num_palet' and
                    r.report_model == 'stock.picking.wave'):
                line_dict = {
                    'package_id': package and package.id,
                    'product_ul_id': ul.id,
                    'report_id': report.report_id.id,
                    'packages_number': 1,
                    'number_copy': report.copy_num,
                    'wave_id': wave.id
                }
                line_id = wiz_line_obj.create(line_dict)
                pack_line_list.append(line_id.id)
        return pack_line_list

    def _charge_by_palet_no_number(
            self, wave, by_palet_no_number, reports, no_pack_line_list):
        wiz_line_obj = self.env['picking.wave.print.label.pack.nonumber']
        for data in by_palet_no_number:
            datos_array = by_palet_no_number[data]
            ul = datos_array['ul']
            qty = datos_array['qty']
            for report in reports.filtered(lambda r: r.label_model == 'palet'):
                line_dict = {
                    'product_ul_id': ul.id,
                    'report_id': report.report_id.id,
                    'packages_number': qty,
                    'number_copy': report.copy_num,
                    'wave_id': wave.id
                }
                line_id = wiz_line_obj.create(line_dict)
                no_pack_line_list.append(line_id.id)
            if not ul:
                continue
            for report in ul.report_ids.filtered(
                    lambda r: r.label_model == 'palet' and
                    r.report_model == 'stock.picking.wave'):
                line_dict = {
                    'product_ul_id': ul.id,
                    'report_id': report.report_id.id,
                    'packages_number': qty,
                    'number_copy': report.copy_num,
                    'wave_id': wave.id
                }
                line_id = wiz_line_obj.create(line_dict)
                no_pack_line_list.append(line_id.id)
        return no_pack_line_list

    @api.one
    def button_print_all(self):
        self.button_print_all_reports()
        self.button_print_all_nonumber_pallet()
        self.button_print_all_number_pallet()
        return {}

    @api.one
    def button_print_all_reports(self):
        print_type = ['server']
        if self.env.user.printing_action == 'server':
            print_type.append('user_default')
        for report in self.report_print.filtered(
                lambda r: r.do_print and r.action_print.type in print_type):
            report.print_reports()
        return {}

    @api.one
    def button_print_all_number_pallet(self):
        print_type = ['server']
        if self.env.user.printing_action == 'server':
            print_type.append('user_default')
        for pallets in self.number_pallet_label_prints.filtered(
                lambda r: r.do_print and r.action_print.type in print_type):
            pallets.print_reports()
        return {}

    @api.one
    def button_print_all_nonumber_pallet(self):
        print_type = ['server']
        if self.env.user.printing_action == 'server':
            print_type.append('user_default')
        for npallets in self.nonumber_pallet_label_prints.filtered(
                lambda r: r.do_print and r.action_print.type in print_type):
            npallets.print_reports()
        return {}
