# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase
from openerp import exceptions


class TestProductPackageLabel(TransactionCase):

    def setUp(self):
        super(TestProductPackageLabel, self).setUp()
        self.report_copy_model = self.env['product.label.report.copy']
        partner_model = self.env['res.partner']
        ul_model = self.env['product.ul']
        self.report_model = self.env['ir.actions.report.xml']
        self.parent = partner_model.create({
            'name': 'Parent Partner',
        })
        self.partner = partner_model.create({
            'name': 'Partner',
            'parent_id': self.parent.id,
        })
        self.product_ul = ul_model.create({
            'name': 'Logistic Unit',
            'type': 'unit',
        })
        self.report = self.report_model.create({
            'name': 'Report',
            'model': 'stock.picking',
            'report_type': 'qweb-pdf',
            'report_name': 'product_package_label.test_report',
        })

    def test_childs_report(self):
        self.partner.write({
            'report_ids': [(0, 0, {
                'report_id': self.report.id,
                'copy_num': 1,
                'label_model': 'palet',
            })]
        })
        self.assertTrue(self.partner.report_ids)
        self.assertEquals(self.parent.childs_report_ids,
                          self.partner.report_ids)

    def test_constraint(self):
        report_copy = self.report_copy_model.create({
            'partner_id': self.partner.id,
            'report_id': self.report.id,
            'copy_num': 1,
            'label_model': 'cube',
        })
        with self.assertRaises(exceptions.ValidationError):
            report_copy.partner_id = False
        with self.assertRaises(exceptions.ValidationError):
            report_copy.write({
                'product_ul_id': self.product_ul.id,
                'partner_id': self.partner.id,
            })
