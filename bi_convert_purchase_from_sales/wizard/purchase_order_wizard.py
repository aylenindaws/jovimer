# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models, _
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class createpurchaseorder(models.TransientModel):
    _name = 'create.purchaseorder'
    _description = "Create Purchase Order"

    new_order_line_ids = fields.One2many('getsale.orderdata', 'new_order_line_id', string="Order Line")
    partner_id = fields.Many2one('res.partner', string='Vendor')
    date_order = fields.Datetime(string='Order Date', required=True, copy=False, default=fields.Datetime.now)

    @api.model
    def default_get(self, default_fields):
        res = super(createpurchaseorder, self).default_get(default_fields)
        data = self.env['sale.order'].browse(self._context.get('active_ids', []))
        update = []
        for record in data.order_line:
            update.append((0, 0, {
                'product_id': record.product_id.id,
                'product_uom': record.product_uom.id,
                'order_id': record.order_id.id,
                'name': record.name,
                'product_qty': record.product_uom_qty,
                'price_unit': record.price_unit,
                'product_subtotal': record.price_subtotal,
                'purchase_price': record.purchase_price,
                'partner_id': record.supplier_id.id if record.supplier_id else False
            }))
        res.update({'new_order_line_ids': update})
        return res

    def action_create_purchase_order(self):
        self.ensure_one()
        res = self.env['purchase.order'].browse(self._context.get('id', []))
        so = self.env['sale.order'].browse(self._context.get('active_id'))
        sale_order_name = so.name
        supplier_list = self.new_order_line_ids.mapped('partner_id')
        for supplier in supplier_list:
            purchase_order_lines = self.new_order_line_ids.filtered(lambda x: x.partner_id.id == supplier.id)
            value = []
            for order_line in purchase_order_lines:
                value.append([0, 0, {
                    'product_id': order_line.product_id.id,
                    'name': order_line.name,
                    'product_qty': order_line.product_qty,
                    'order_id': order_line.order_id.id,
                    'sale_line_id': order_line.id,
                    'product_uom': order_line.product_uom.id,
                    'taxes_id': order_line.product_id.supplier_taxes_id.ids,
                    'date_planned': order_line.date_planned,
                    'price_unit': order_line.purchase_price,
                }])
            res.create({
                'partner_id': supplier.id,
                'date_order': str(self.date_order),
                'order_line': value,
                'origin': sale_order_name,
                'sale_related_id': so.id,
                'partner_ref': sale_order_name,
                'fiscal_position_id': supplier.property_account_position_id.id if supplier.property_account_position_id else False
            })


class Getsaleorderdata(models.TransientModel):
    _name = 'getsale.orderdata'
    _description = "Get Sale Order Data"

    new_order_line_id = fields.Many2one('create.purchaseorder')

    product_id = fields.Many2one('product.product', string="Product")
    name = fields.Char(string="Description")
    product_qty = fields.Float(string='Quantity', required=True)
    date_planned = fields.Datetime(string='Scheduled Date', default=datetime.today())
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    order_id = fields.Many2one('sale.order', string='Order Reference', ondelete='cascade', index=True)
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    product_subtotal = fields.Float(string="Sub Total", compute='_compute_total')
    purchase_price = fields.Float(string="Purchase price")
    partner_id = fields.Many2one('res.partner', string="Supplier")

    @api.depends('product_qty', 'price_unit')
    def _compute_total(self):
        for record in self:
            record.product_subtotal = record.product_qty * record.price_unit
