# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import exceptions


class TestMrpProductionAddMiddleStuff(common.TransactionCase):

    def setUp(self):
        super(TestMrpProductionAddMiddleStuff, self).setUp()
        production_model = self.env['mrp.production']
        product_model = self.env['product.product']
        unit_uom = self.browse_ref('product.product_uom_unit')
        self.unit_kg = self.browse_ref('product.product_uom_kgm')
        product = product_model.create({
            'name': 'Production Product',
            'uom_id': unit_uom.id,
        })
        self.product1 = product_model.create({
            'name': 'Consume Product',
            'uom_id': unit_uom.id,
        })
        bom = self.env['mrp.bom'].create({
            'product_tmpl_id': product.product_tmpl_id.id,
            'product_id': product.id,
            'bom_line_ids': [(0, 0, {
                'product_id': self.product1.id,
                'product_qty': 1.0,
                'product_uom': self.product1.uom_id.id,
            })]
        })
        self.production = production_model.create({
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'bom_id': bom.id,
        })
        self.adj_model = self.env['mrp.production.adjustment.line.wizard']
        self.production.action_compute()
        self.production.action_confirm()

    def test_adjustment(self):
        self.assertFalse(self.production.adjustment_ids)
        self.assertFalse(self.production.product_lines.filtered('addition'))
        self.assertEquals(len(self.production.move_lines), 1)
        wiz_values = {
            'product_id': self.product1.id,
            'product_qty': 0.0,
            'product_uom_id': self.unit_kg.id,
        }
        with self.assertRaises(exceptions.ValidationError):
            self.adj_model.with_context(
                active_id=self.production.id).create(wiz_values)
        wiz_values.update({'product_uom_id': self.product1.uom_id.id})
        with self.assertRaises(exceptions.ValidationError):
            self.adj_model.with_context(
                active_id=self.production.id).create(wiz_values)
        wiz_values.update({'product_qty': 1.0})
        add_wiz = self.adj_model.with_context(
            active_id=self.production.id).create(wiz_values)
        add_wiz.make_adjustment()
        self.assertTrue(self.production.adjustment_ids)
        self.assertTrue(self.production.product_lines.filtered('addition'))
        self.assertEquals(len(self.production.move_lines), 2)

    def test_adjustment_onchange(self):
        wiz_values = {
            'product_id': self.product1.id,
        }
        adj_wiz = self.adj_model.with_context(
            active_id=self.production.id).new(wiz_values)
        self.assertFalse(adj_wiz.product_qty)
        self.assertFalse(adj_wiz.product_uom_id)
        adj_wiz.onchange_product_id()
        self.assertEquals(adj_wiz.product_qty, 1.0)
        self.assertEquals(adj_wiz.product_uom_id, self.product1.uom_id)
