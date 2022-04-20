# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import odoo.addons.decimal_precision as dp
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    paleteur = fields.Float(string='Eur', compute='_compute_palet_type', default=0)
    paletgr = fields.Float(string='Gr', compute='_compute_palet_type', default=0)
    totalbultos = fields.Float(string='Total Bultos', compute='_compute_palet_type', default=0)
    supplier_id = fields.Many2one('res.partner', string="Proveedor", compute='_compute_sale_order')
    stock_check = fields.Boolean("Stock", default=False)
    client_id = fields.Many2one('res.partner', string='Cliente', compute='_compute_sale_order')
    variedad = fields.Many2one('jovimer.variedad', string='Variedad', compute='_compute_sale_order')
    confeccion = fields.Many2one('jovimer.confeccion', string='Confección', compute='_compute_sale_order')
    envase = fields.Many2one('jovimer.envase', string='Envase')
    cantidadpedido = fields.Float(string='Palets Venta', digits=None, default=0)
    tipouom = fields.Many2one('jovimer.palet', string='Tipo Palet')
    costetrans = fields.Float(string='Transporte')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Expediente', index=True, compute='_compute_sale_order')
    fechasalida = fields.Date(string='Fecha de Carga')
    fechallegada = fields.Date(string='Fecha de Descarga')

    @api.model
    def create(self, vals):
        if 'purchase_line_id' in vals:
            purchase_line_id = self.env['purchase.order.line'].search([('id', '=', vals['purchase_line_id'])])
            if purchase_line_id.sale_line_id:
                vals['product_uom_qty'] = purchase_line_id.sale_line_id.product_uom_qty
        result = super(StockMove, self).create(vals)
        return result

    # @api.depends('sale_line_id')
    @api.depends('purchase_line_id')
    def _compute_palet_type(self):
        for item in self:
            # if item.sale_line_id:
            if item.purchase_line_id.order_id.sale_related_id and item.purchase_line_id.order_id.sale_related_id.order_line:
                for order_line in item.purchase_line_id.order_id.sale_related_id.order_line:
                    if item.product_id == order_line.product_id:
                        if order_line.tipouom:
                            if 'EUR' in order_line.tipouom.name or 'GREENBOX' in order_line.tipouom.name:
                                item.write({'paleteur': order_line.cantidadpedido})
                                item.write({'paletgr': 0})
                            if 'Grande' in order_line.tipouom.name:
                                item.write({'paletgr': order_line.cantidadpedido})
                                item.write({'paleteur': 0})
                            item.totalbultos = order_line.bultos
                        else:
                            item.write({'paletgr': 0, 'paleteur': 0, 'totalbultos': 0})
            else:
                item.write({'paletgr': 0, 'paleteur': 0, 'totalbultos': 0})

    def _set_product_qty(self):
        raise ValidationError('Inverse de product_qty para stock.move')

    @api.depends('purchase_line_id')
    def _compute_sale_order(self):
        ok = True
        for item in self:
            for order_line in item.purchase_line_id.order_id.sale_related_id.order_line:
                if item.product_id == order_line.product_id:
                    self.supplier_id = order_line.supplier_id
                    self.client_id = order_line.partner_id
                    self.analytic_account_id = item.purchase_line_id.order_id.sale_related_id.analytic_account_id
                    self.variedad = order_line.variedad
                    self.confeccion = order_line.confeccion
                    ok = False
            if ok:
                self.supplier_id = None
                self.client_id = None
                self.analytic_account_id = None
                self.variedad = None
                self.confeccion = None


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    product_qty = fields.Float('Cantidad', digits=dp.get_precision('Product Unit of Measure'), store=True, copy=False)

    def _set_product_qty(self):
        raise ValidationError('Inverse de product_qty para stock.move.line')