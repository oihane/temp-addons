# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import _, api, fields, models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    @api.model
    def _get_action(self):
        return [('packaging', _('Packaging'))] +\
            super(ProcurementRule, self)._get_action()


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    packop_id = fields.Many2one(
        comodel_name='packaging.operation', string='Packaging Line')

    @api.one
    def propagate_cancel(self):
        if self.rule_id.action == 'packaging' and \
                self.packop_id.packaging_production:
            self.packop_id.packaging_production.action_cancel()
        return super(ProcurementOrder, self).propagate_cancel()

    @api.model
    def _check(self, procurement):
        if procurement.packop_id and procurement.packop_id.processed and \
                procurement.packop_id.packaging_production.state == 'done':
            # TOCHECK: no better method?
            return True
        return super(ProcurementOrder, self)._check(procurement)

    @api.model
    def _run(self, procurement):
        if procurement.rule_id and procurement.rule_id.action == 'packaging':
            # make a packaging operation for the procurement
            return procurement.make_packop()[procurement.id]
        return super(ProcurementOrder, self)._run(procurement)

    @api.multi
    def check_production_exists(self):
        """ Finds the manufacturing order for the product from procurement
        order.
        @return: production
        """
        for procurement in self:
            bom_obj = self.env['mrp.bom']
            if procurement.bom_id:
                bom_id = procurement.bom_id.id
            else:
                properties = [x.id for x in procurement.property_ids]
                bom_id = bom_obj.with_context(
                    company_id=procurement.company_id.id)._bom_find(
                    product_id=procurement.product_id.id,
                    properties=properties)
            bom = bom_obj.browse(bom_id)
            value = procurement.product_id.attribute_value_ids.filtered(
                'raw_product')
            fill = (value[:1].numeric_value or 1) * procurement.product_qty
            productions = self.env['mrp.production']
            for product in bom.bom_line_ids.mapped('product_id'):
                productions |= self.env['mrp.production'].search(
                    [('product_id', '=', product.id),
                     ('production', '=', False), ('state', '!=', 'cancel'),
                     ('left_product_qty', '>=', fill)])
                if productions:
                    continue
            return productions and productions[0]
        return False

    @api.model
    def _prepare_packop_vals(self, procurement, production):
        res_id = procurement.move_dest_id and procurement.move_dest_id.id or\
            False
        value = procurement.product_id.attribute_value_ids.filtered(
            'raw_product')
        fill = (value[:1].numeric_value or 1) * procurement.product_qty
        return {
            'operation': production.id,
            'product': procurement.product_id.id,
            'qty': procurement.product_qty,
            'fill': fill,
            'move_prod_id': res_id,
        }

    @api.multi
    def make_packop(self):
        """ Make Manufacturing(production) order from procurement
        @return: New created Production Orders procurement wise
        """
        res = {}
        packaging_obj = self.env['packaging.operation']
        for procurement in self:
            if self.check_bom_exists():
                production = self.check_production_exists()
                if production:
                    # create the packaging as SUPERUSER because the current
                    # user may not have the rights to do it (mto product
                    # launched by a sale for example)
                    vals = self._prepare_packop_vals(procurement, production)
                    packop = packaging_obj.sudo().create(vals)
                    res[procurement.id] = packop.id
                    procurement.write({'packop_id': packop.id})
                    self.packaging_create_note(procurement)
                else:
                    res[procurement.id] = False
                    procurement.message_post(
                        body=_('No manufacturing order found to package '
                               'this product!'))
            else:
                res[procurement.id] = False
                procurement.message_post(
                    body=_("No BoM exists for this product!"))
        return res

    @api.model
    def packaging_create_note(self, procurement, context=None):
        body = _("Packaging line created.")
        procurement.message_post(body=body)
