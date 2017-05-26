# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import _, api, exceptions, fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    package_to_resupply = fields.Boolean(
        string='Package in this Warehouse', default=True,
        help="When products are packaged, they can be packaged in this"
        " warehouse.")
    package_pull_id = fields.Many2one(
        comodel_name='procurement.rule', string='Packaging Rule')

    @api.one
    def _get_package_pull_rule(self):
        route_obj = self.env['stock.location.route']
        data_obj = self.env['ir.model.data']
        try:
            package_route_id = data_obj.get_object_reference(
                'sale_mrp_packaging', 'route_warehouse0_packaging')[1]
        except:
            package_route_id =\
                route_obj.search([('name', 'like', _('Packaging'))])
            package_route_id =\
                package_route_id and package_route_id[0] or False
        if not package_route_id:
            raise exceptions.Warning(
                _('Error!'), _('Can\'t find any generic Package route.'))

        return {
            'name': self._format_routename(self, _(' Packaging')),
            'location_id': self.lot_stock_id.id,
            'route_id': package_route_id,
            'action': 'packaging',
            'picking_type_id': self.int_type_id.id,
            'propagate': False,
            'warehouse_id': self.id,
        }

    @api.one
    def create_routes(self):
        pull_obj = self.env['procurement.rule']
        res = super(StockWarehouse, self).create_routes()
        if self.package_to_resupply:
            package_pull_vals = self._get_package_pull_rule()
            package_pull_id = pull_obj.create(package_pull_vals[0])
            res['package_pull_id'] = package_pull_id.id
        return res

    @api.multi
    def write(self, vals):
        pull_obj = self.env['procurement.rule']
        if 'package_to_resupply' in vals:
            if vals.get("package_to_resupply"):
                for warehouse in self:
                    if not warehouse.package_pull_id:
                        package_pull_vals = warehouse._get_package_pull_rule()
                        package_pull_id = pull_obj.create(package_pull_vals[0])
                        vals['package_pull_id'] = package_pull_id.id
            else:
                for warehouse in self:
                    if warehouse.package_pull_id:
                        warehouse.package_pull_id.unlink()
        return super(StockWarehouse, self).write(vals)

    @api.model
    def get_all_routes_for_wh(self, warehouse):
        all_routes = super(StockWarehouse, self).get_all_routes_for_wh(
            warehouse)
        if warehouse.package_to_resupply and warehouse.package_pull_id and\
                warehouse.package_pull_id.route_id:
            all_routes += [warehouse.package_pull_id.route_id.id]
        return all_routes

    @api.model
    def _handle_renaming(self, warehouse, name, code):
        res = super(StockWarehouse, self)._handle_renaming(
            warehouse, name, code)
        # change the package pull rule name
        if warehouse.package_pull_id:
            warehouse.package_pull_id.write(
                {'name': warehouse.package_pull_id.name.replace(
                    warehouse.name, name, 1)})
        return res

    @api.one
    def _get_all_products_to_resupply(self):
        product_obj = self.env['product.product']
        res = super(StockWarehouse, self)._get_all_products_to_resupply()
        if self.package_pull_id and self.package_pull_id.route_id:
            for product_id in res:
                for route in product_obj.browse(product_id).route_ids:
                    if route.id == self.package_pull_id.route_id.id:
                        res.remove(product_id)
                        break
        return res
