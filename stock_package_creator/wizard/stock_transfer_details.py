# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.model
    def default_get(self, fields):
        picking_obj = self.env['stock.picking']
        package_capacity = {}
        result = super(StockTransferDetails, self).default_get(fields)
        if self.env.context.get('active_model') == 'stock.picking':
            picking = picking_obj.browse(self.env.context['active_id'])
        if 'origin_wave' not in self.env.context:
            if picking.picking_type_id.code != 'outgoing':
                return result
        for item in result['item_ids']:
            try:
                picking = picking_obj.browse(item['picking_id'])
            except:
                pass
            partner = picking.partner_id.parent_id or picking.partner_id
            product = self.env['product.product'].browse(item['product_id'])
            suppinfo = self.env['product.supplierinfo'].search([
                ('product_tmpl_id', '=', product.product_tmpl_id.id),
                ('name', '=', partner.id), ('ul_id', '!=', False)
            ])
            item.update({'pallet_ul': suppinfo[:1].ul_id.id})
            package_capacity = self._catch_package_capacity(
                package_capacity, item['product_id'], item['pallet_ul'])
        result.update({'item_ids': self._calculate_new_item_ids(
                       result['item_ids'], package_capacity)})
        return result

    @api.multi
    def _catch_package_capacity(self, package_capacity, product_id,
                                product_ul_id):
        try:
            found = package_capacity[(product_id, product_ul_id)]
        except:
            found = False
        if not found:
            tcapacity = self._calculate_package_capacity(
                product_id, product_ul_id)
            if tcapacity:
                my_vals = {
                    'tproduct_id': product_id,
                    'tproduct_ul': product_ul_id,
                    'tcapacity': tcapacity,
                }
                package_capacity[(product_id, product_ul_id)] = my_vals
        return package_capacity

    @api.multi
    def _calculate_package_capacity(self, product_id, product_ul_id):
        product = self.env['product.product'].browse(product_id)
        product_ul = self.env['product.ul'].browse(product_ul_id)
        units_package = False
        for attr_value in product.attribute_value_ids.filtered(
                lambda r: r.attribute_id.is_package):
            for packaging in product_ul.packagings.filtered(
                    lambda p: p.product == attr_value.package_product):
                units_package = \
                    packaging.ul_qty * packaging.rows *\
                    attr_value.numeric_value
        return units_package

    @api.multi
    def _calculate_new_item_ids(self, item_ids, package_capacity):
        new_item_ids = [] if package_capacity else item_ids
        picking_obj = self.env['stock.picking']
        product_ul_obj = self.env['product.ul']
        if self.env.context.get('active_model') == 'stock.picking':
            picking = picking_obj.browse(self.env.context.get('active_id'))
        for item in item_ids:
            try:
                picking = picking_obj.browse(item['picking_id'])
            except:
                pass
            pack = picking.picking_type_id.code == 'outgoing' and \
                picking.picking_type_id.pack
            product_ul = product_ul_obj.browse(item['pallet_ul'])
            try:
                datos_array = package_capacity[(
                    item['product_id'], item['pallet_ul'])]
                tcapacity = datos_array['tcapacity']
            except:
                tcapacity = False
            if pack and ((not tcapacity and not item['result_package_id']) or
                         (tcapacity and item['result_package_id'])):
                new_item = item.copy()
                new_item_ids.append(new_item)
            elif pack and tcapacity and not item['result_package_id']:
                package = product_ul.create_quant_pck_from_ul()
                pending_qty = item['quantity'] - tcapacity
                new_item = item.copy()
                new_item.update({
                    'quantity': tcapacity,
                    'result_package_id': (package and package.id)
                })
                new_item_ids.append(new_item)
                while pending_qty > 0:
                    package = product_ul.create_quant_pck_from_ul()
                    new_item = item.copy()
                    new_item.update({
                        'result_package_id': (package and package.id),
                        'packop_id': False,
                        'quantity': tcapacity if pending_qty > tcapacity
                        else pending_qty,
                    })
                    new_item_ids.append(new_item)
                    pending_qty -= tcapacity
        return new_item_ids


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    pallet_ul = fields.Many2one(
        comodel_name='product.ul', string='Pallet UL')
