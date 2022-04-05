# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models, _
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class createpurchaseorder(models.TransientModel):
    _inherit = 'create.purchaseorder'

    @api.model
    def default_get(self, default_fields):
        res = super(createpurchaseorder, self).default_get(default_fields)
        data = self.env['sale.order'].browse(self._context.get('active_ids', []))
        update = []
        for record in data.order_line:
            update.append((0, 0, {
                'product_id': record.product_id.id,
                'product_uom': record.uom_po_id.id,
                'order_id': record.order_id.id,
                'name': record.name,
                'product_qty': record.on_change_cantidadpedido_purchase(record.product_uom.name, record.uom_po_id.name),
                'price_unit': record.price_unit,
                'product_subtotal': record.price_subtotal,
                'discount': record.discount_supplier,
                'purchase_price': record.purchase_price,
                'cantidadpedido': record.cantidadpedido,
                'tipouom': record.tipouom.id,
                'bultos': record.bultos,
                'variedad': record.variedad.id,
                'confeccion': record.confeccion.id,
                'calibre': record.calibre.id,
                'marca': record.marca.id,
                'envase': record.envase.id,
                'account_analytic_id': data.analytic_account_id.id,
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
                    'product_uom': order_line.product_uom.id,
                    'taxes_id': order_line.product_id.supplier_taxes_id.ids,
                    'date_planned': order_line.date_planned,
                    'price_unit': order_line.purchase_price,
                    'cantidadpedido': order_line.cantidadpedido,
                    'tipouom': order_line.tipouom.id,
                    'bultos': order_line.bultos,
                    'variedad': order_line.variedad.id,
                    'confeccion': order_line.confeccion.id,
                    'calibre': order_line.calibre.id,
                    'marca': order_line.marca.id,
                    'envase': order_line.envase.id,
                    'discount': order_line.discount,
                    'account_analytic_id': order_line.account_analytic_id.id,
                }])
            res.create({
                'partner_id': supplier.id,
                'date_order': str(self.date_order),
                'order_line': value,
                'origin': sale_order_name,
                'fechallegada':so.commitment_date,
                'sale_related_id': so.id,
                'partner_ref': sale_order_name,
                'fiscal_position_id': supplier.property_account_position_id.id if supplier.property_account_position_id else False
            })


class Getsaleorderdata(models.TransientModel):
    _inherit = 'getsale.orderdata'

    cantidadpedido = fields.Float(string='Cantidad Pedido')
    tipouom = fields.Many2one('jovimer.palet', string='Tipo Medida')
    bultos = fields.Float(string='Bultos')
    variedad = fields.Many2one('jovimer.variedad', string='Variedad')
    confeccion = fields.Many2one('jovimer.confeccion', string='Confección')
    calibre = fields.Many2one('jovimer.calibre', string='Calibre')
    marca = fields.Many2one('jovimer.marca', string='Marca')
    envase = fields.Many2one('jovimer.envase', string='Envase')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Expediente')
    discount = fields.Float(string="Descuento", digits="Discount")