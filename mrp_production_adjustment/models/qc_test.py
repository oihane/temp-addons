# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class QcTestCategory(models.Model):
    _inherit = 'qc.test.category'

    adjustment_test = fields.Boolean()


class QcTest(models.Model):
    _inherit = 'qc.test'

    adjustment_test = fields.Boolean(related='category.adjustment_test')
