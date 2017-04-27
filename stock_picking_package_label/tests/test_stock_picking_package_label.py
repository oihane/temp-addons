# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.product_package_label.tests import \
    test_product_package_label


class TestStockPickingPackageLabel(
        test_product_package_label.TestProductPackageLabel):

    def setUp(self):
        super(TestStockPickingPackageLabel, self).setUp()
        stock_picking_model = self.env['stock.picking']
        self.product = self.browse_ref('product.product_product_46')
        self.report.write({
            'property_printing_action': self.ref(
                'base_report_to_printer.printing_action_1'),
        })
        self.report2 = self.report_model.create({
            'name': 'Report',
            'model': 'stock.pack.operation',
            'report_type': 'qweb-pdf',
            'report_name': 'stock_picking_package_label.test_report',
            'property_printing_action': self.ref(
                'base_report_to_printer.printing_action_1'),
        })
        picking_type = self.browse_ref('stock.picking_type_out')
        self.stock_picking = stock_picking_model.create({
            'partner_id': self.partner.id,
            'picking_type_id': picking_type.id,
            'move_lines': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 1.0,
                'product_uom': self.product.uom_id.id,
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': picking_type.default_location_dest_id.id,
            })],
        })
        self.stock_picking.action_confirm()

    def test_stock_picking_package_label(self):
        self.report_copy_model.create({
            'partner_id': self.partner.id,
            'report_id': self.report.id,
            'copy_num': 1,
            'label_model': 'picking',
        })
        self.report_copy_model.create({
            'partner_id': self.partner.id,
            'report_id': self.report2.id,
            'copy_num': 1,
            'label_model': 'cube',
        })
        # self.stock_picking.button_load_printing_info()
        # self.stock_picking.button_print_all()

    def test_childs_report(self):
        """ pass """

    def test_constraint(self):
        """ pass """
