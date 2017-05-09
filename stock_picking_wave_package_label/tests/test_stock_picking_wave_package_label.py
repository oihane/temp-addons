# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.stock_picking_package_label.tests import \
    test_stock_picking_package_label


class TestStockPickingWavePackageLabel(
        test_stock_picking_package_label.TestStockPickingPackageLabel):

    def setUp(self):
        super(TestStockPickingWavePackageLabel, self).setUp()
        stock_picking_wave_model = self.env['stock.picking.wave']
        self.report3 = self.report_model.create({
            'name': 'Report',
            'model': 'stock.picking.wave',
            'report_type': 'qweb-pdf',
            'report_name': 'stock_picking_wave_package_label.test_report',
            'property_printing_action': self.ref(
                'base_report_to_printer.printing_action_1'),
        })
        self.wave = stock_picking_wave_model.create({
            'partner': self.partner.id,
            'picking_ids': [(6, 0, self.stock_picking.ids)],
        })

    def test_stock_picking_wave_package_label(self):
        self.assertFalse(self.wave.report_print)
        self.assertFalse(self.wave.number_pallet_label_prints)
        self.assertFalse(self.wave.nonumber_pallet_label_prints)
        self.fix_report_view(self.report3)
        self.report_copy_model.create({
            'partner_id': self.partner.id,
            'report_id': self.report3.id,
            'copy_num': 1,
            'label_model': 'wave',
        })
        self.wave.button_load_printing_info()
        self.assertTrue(self.wave.report_print)
        # self.assertTrue(self.wave.number_pallet_label_prints)
        # self.assertTrue(self.wave.nonumber_pallet_label_prints)
        self.wave.button_print_all()

    def test_stock_picking_package_label(self):
        """ pass """
