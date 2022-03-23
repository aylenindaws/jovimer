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
    qty_received = fields.Float(string="Cantidad Recibida", digits=dp.get_precision('Product Unit of Measure'),copy=False)
    qty_invoiced = fields.Float(string="Cantidad Facturada", digits=dp.get_precision('Product Unit of Measure'),store=True)
    discount = fields.Float(string='Descuento (%)', digits=dp.get_precision('Discount'))

    def save_change(self):
        for item in self:
            item.order_line_id.type_state = 'grinding'
            item.order_line_id.price_unit = item.price_unit
            item.order_line_id.discount = item.discount