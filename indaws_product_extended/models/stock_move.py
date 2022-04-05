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

    paleteur = fields.Float(string='Eur', compute='_compute_palet_type', default=0, store=True)
    paletgr = fields.Float(string='Gr', compute='_compute_palet_type', default=0, store=True)
    totalbultos = fields.Float(string='Total Bultos', compute='_compute_palet_type', default=0, store=True)
    supplier_id = fields.Many2one('res.partner', string="Proveedor")
    stock_check = fields.Boolean("Stock", default=False)
    client_id = fields.Many2one('res.partner', string='Cliente')
    variedad = fields.Many2one('jovimer.variedad', string='Variedad')
    confeccion = fields.Many2one('jovimer.confeccion', string='Confección')
    envase = fields.Many2one('jovimer.envase', string='Envase')
    cantidadpedido = fields.Float(string='Palets Venta', digits=None, default=0)
    tipouom = fields.Many2one('jovimer.palet', string='Tipo Palet')
    costetrans = fields.Float(string='Transporte')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Expediente', index=True)
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

    @api.depends('sale_line_id')
    def _compute_palet_type(self):
        for item in self:
            if item.sale_line_id:
                if item.sale_line_id.tipouom:
                    if 'EUR' in item.sale_line_id.tipouom.name or 'GREENBOX' in item.sale_line_id.tipouom.name:
                        item.write({'paleteur': item.sale_line_id.cantidadpedido})
                        item.write({'paletgr': 0})
                    if 'Grande' in item.sale_line_id.tipouom.name:
                        item.write({'paletgr': item.sale_line_id.cantidadpedido})
                        item.write({'paleteur': 0})
                    item.totalbultos = item.sale_line_id.bultos
                else:
                    item.write({'paletgr': 0, 'paleteur': 0, 'totalbultos': 0})

    def _set_product_qty(self):
        raise ValidationError('Inverse de product_qty para stock.move')


class StockMove(models.Model):
    _inherit = 'stock.move.line'

    product_qty = fields.Float('Cantidad', digits=dp.get_precision('Product Unit of Measure'), store=True, copy=False)

    def _set_product_qty(self):
        raise ValidationError('Inverse de product_qty para stock.move.line')