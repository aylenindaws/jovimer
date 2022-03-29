# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models, _
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class PurchaseOrderLineWizard(models.TransientModel):
    _name = 'purchase.order.line.wizard'
    _description = "Cuenta de Venta"

    order_line_id = fields.Many2one('purchase.order.line', string="Linea de Cuenta de Venta")
    product_id = fields.Many2one('product.product', string="Producto")
    price_unit = fields.Float(string='Precio Unitario', digits='Product Price')
    product_qty = fields.Float('Cantidad', digits=dp.get_precision('Product Unit of Measure'),store=True,copy=False)
    qty_received = fields.Float(string="Cantidad Recibida", digits=dp.get_precision('Product Unit of Measure'),copy=False)
    qty_invoiced = fields.Float(string="Cantidad Facturada", digits=dp.get_precision('Product Unit of Measure'),store=True)
    discount = fields.Float(string='Descuento (%)', digits=dp.get_precision('Discount'))
    track = fields.Text('Cambios Realizados')

    @api.onchange('price_unit','discount','product_qty')
    def _onchange_track(self):
        for item in self:
            if not item.order_line_id.track:
                item.order_line_id.track = ''
            item.track = item.order_line_id.track
            if item.discount != item.order_line_id.discount:
                item.track = item.track + " - Modificación de Descuento de: " + str(item.order_line_id.discount) + " a " + str(item.discount)
            if item.price_unit != item.order_line_id.price_unit:
                item.track = item.track + " - Modificación de Precio Unitario de: " + str(item.order_line_id.price_unit) + " a " + str(item.price_unit)
            if item.product_qty != item.order_line_id.product_qty:
                item.track = item.track + " - Modificación de Cantidad de: " + str(item.order_line_id.product_qty) + " a " + str(item.product_qty)

    def save_change(self):
        for item in self:
            item.order_line_id.write({
                'type_state': 'grinding',
                'price_unit': item.price_unit,
                'discount': item.discount,
                'product_qty': item.product_qty,
                'track': item.track
            })