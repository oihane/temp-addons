# -*- coding: utf-8 -*-
# Copyright © 2015-2017 AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import math
from openerp import models, fields, api


class ProductLabelReportCopy(models.Model):
    _inherit = 'product.label.report.copy'

    label_model = fields.Selection(selection_add=[('picking', 'Picking')])


class PickingPrintReport(models.Model):
    _name = 'picking.print.report'

    picking_id = fields.Many2one(
        comodel_name='stock.picking', string='Picking',
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
        return self.print_copies(self.picking_id, self.number_copy)

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


class PickingPrintLabelCube(models.Model):
    _name = 'picking.print.label.cube'
    _inherit = 'picking.print.report'

    lot_id = fields.Many2one(
        comodel_name='stock.production.lot', string='Lot/Serial Number')
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product')
    product_qty = fields.Float(string='Qty')
    cubes_number = fields.Float(string='# Cubes')
    operation_id = fields.Many2one(
        comodel_name='stock.pack.operation', string='Operation',
        ondelete='cascade')

    @api.multi
    def print_reports(self):
        self.ensure_one()
        return self.print_copies(self.operation_id,
                                 self.number_copy * self.cubes_number)


class PickingPrintLabelPackNumber(models.Model):
    _name = 'picking.print.label.pack.number'
    _inherit = 'picking.print.report'

    package_id = fields.Many2one(
        comodel_name='stock.quant.package', string='Package')
    product_ul_id = fields.Many2one(
        comodel_name='product.ul', string='Product Ul')
    packages_number = fields.Float(string='# Pallets')

    @api.multi
    def print_reports(self):
        self.ensure_one()
        return self.print_copies(self.picking_id,
                                 self.number_copy * self.packages_number)


class PickingPrintLabelPackNonumber(models.Model):
    _name = 'picking.print.label.pack.nonumber'
    _inherit = 'picking.print.report'

    product_ul_id = fields.Many2one(
        comodel_name='product.ul', string='Product Ul')
    packages_number = fields.Float(string='# Pallets')

    @api.multi
    def print_reports(self):
        self.ensure_one()
        return self.print_copies(self.picking_id,
                                 self.number_copy * self.packages_number)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    report_print = fields.One2many(
        comodel_name='picking.print.report', inverse_name='picking_id',
        string='Reports')
    cube_label_prints = fields.One2many(
        comodel_name='picking.print.label.cube', inverse_name='picking_id',
        string='By Cubes')
    number_pallet_label_prints = fields.One2many(
        comodel_name='picking.print.label.pack.number',
        inverse_name='picking_id', string='By Pallet Numbers')
    nonumber_pallet_label_prints = fields.One2many(
        comodel_name='picking.print.label.pack.nonumber',
        inverse_name='picking_id', string='By Logistic Unit')

    @api.one
    def button_load_printing_info(self):
        self.cube_label_prints.unlink()
        self.number_pallet_label_prints.unlink()
        self.nonumber_pallet_label_prints.unlink()
        self.report_print.unlink()
        if not self.pack_operation_ids:
            self.do_prepare_partial()
        by_palet_number = {}
        by_palet_no_number = {}
        line_list = []
        pack_line_list = []
        no_pack_line_list = []
        report_print_list = []
        partners = self.partner_id | self.partner_id.commercial_partner_id
        reports = partners.mapped('report_ids')
        cube_reports = reports.filtered(
            lambda r: r.label_model == 'cube' and
            r.report_model == 'stock.pack.operation')
        palet_reports = reports.filtered(
            lambda r: r.label_model in ['palet', 'num_palet'] and
            r.report_model == 'stock.picking')
        picking_reports = reports.filtered(
            lambda r: r.label_model == 'picking' and
            r.report_model == 'stock.picking')
        for operation in self.pack_operation_ids:
            by_palet_number, by_palet_no_number = (
                self._calc_by_palet(
                    operation, by_palet_number, by_palet_no_number))
            line_list = self._charge_by_cubes(
                operation, cube_reports, line_list)
        if by_palet_number:
            pack_line_list = self._charge_by_palet_number(
                self, by_palet_number, palet_reports, pack_line_list)
        if by_palet_no_number:
            no_pack_line_list = self._charge_by_palet_no_number(
                self, by_palet_no_number, palet_reports, no_pack_line_list)
        for print_report in picking_reports:
            picking_print = self.report_print.create({
                'picking_id': self.id,
                'report_id': print_report.report_id.id,
                'number_copy': print_report.copy_num,
            })
            report_print_list.append(picking_print.id)
        self.report_print = report_print_list
        self.cube_label_prints = line_list
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

    def _charge_by_cubes(self, operation, reports, line_list):
        wiz_line_obj = self.env['picking.print.label.cube']
        pack_attr = operation.product_id.attribute_value_ids.filtered(
            lambda x: x.attribute_id.is_package)
        for report in reports:
            line = wiz_line_obj.browse(line_list).filtered(
                lambda x: x.lot_id == operation.lot_id and
                x.report_id == report.report_id)[:1]
            if not line:
                line_dict = {
                    'lot_id': operation.lot_id.id,
                    'product_id': operation.product_id.id,
                    'product_qty': operation.product_qty,
                    'report_id': report.report_id.id,
                    'cubes_number': math.ceil(operation.product_qty /
                                              (pack_attr and
                                               pack_attr.numeric_value or
                                               1.0)),
                    'number_copy': report.copy_num,
                    'picking_id': self.id,
                    'operation_id': operation.id,
                }
                line_id = wiz_line_obj.create(line_dict)
                line_list.append(line_id.id)
            else:
                line.product_qty += operation.product_qty
                line.cubes_number += math.ceil(
                    operation.product_qty /
                    (pack_attr and pack_attr.numeric_value or 1.0))
        return line_list

    def _charge_by_palet_number(
            self, picking, by_palet_number, reports, pack_line_list):
        wiz_line_obj = self.env['picking.print.label.pack.number']
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
                    'picking_id': picking.id
                }
                line_id = wiz_line_obj.create(line_dict)
                pack_line_list.append(line_id.id)
            if not ul:
                continue
            for report in ul.report_ids.filtered(
                    lambda r: r.label_model == 'num_palet' and
                    r.report_model == 'stock.picking'):
                line_dict = {
                    'package_id': package and package.id,
                    'product_ul_id': ul.id,
                    'report_id': report.report_id.id,
                    'packages_number': 1,
                    'number_copy': report.copy_num,
                    'picking_id': picking.id
                }
                line_id = wiz_line_obj.create(line_dict)
                pack_line_list.append(line_id.id)
        return pack_line_list

    def _charge_by_palet_no_number(
            self, picking, by_palet_no_number, reports, no_pack_line_list):
        wiz_line_obj = self.env['picking.print.label.pack.nonumber']
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
                    'picking_id': picking.id
                }
                line_id = wiz_line_obj.create(line_dict)
                no_pack_line_list.append(line_id.id)
            for report in ul.report_ids.filtered(
                    lambda r: r.label_model == 'palet' and
                    r.report_model == 'stock.picking'):
                line_dict = {
                    'product_ul_id': ul.id,
                    'report_id': report.report_id.id,
                    'packages_number': qty,
                    'number_copy': report.copy_num,
                    'picking_id': picking.id
                }
                line_id = wiz_line_obj.create(line_dict)
                no_pack_line_list.append(line_id.id)
        return no_pack_line_list

    @api.one
    def button_print_all(self):
        self.button_print_all_reports()
        self.button_print_all_cube()
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
    def button_print_all_cube(self):
        print_type = ['server']
        if self.env.user.printing_action == 'server':
            print_type.append('user_default')
        for cube in self.cube_label_prints.filtered(
                lambda r: r.do_print and r.action_print.type in print_type):
            cube.print_reports()
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
