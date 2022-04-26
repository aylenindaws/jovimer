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
    supplier_id = fields.Many2one('res.partner', string="Proveedor", related='purchase_line_id.order_id.partner_id')
    stock_check = fields.Boolean("Stock", default=False)
    client_id = fields.Many2one('res.partner', string='Cliente', related='sale_line_id.order_id.partner_id')
    variedad = fields.Many2one('jovimer.variedad', string='Variedad', related='sale_line_id.variedad')
    confeccion = fields.Many2one('jovimer.confeccion', string='Confección', related='sale_line_id.confeccion')
    envase = fields.Many2one('jovimer.envase', string='Envase', related='sale_line_id.envase')
    cantidadpedido = fields.Float(string='Palets Venta', digits=None, related='sale_line_id.cantidadpedido')
    tipouom = fields.Many2one('jovimer.palet', string='Tipo Palet', related='sale_line_id.tipouom')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Expediente', index=True, related='sale_line_id.order_id.analytic_account_id')
    fechasalida = fields.Date(string='Fecha de Carga')
    fechallegada = fields.Date(string='Fecha de Descarga')
    picking_type_id_code = fields.Selection([('incoming', 'Receipt'), ('outgoing', 'Delivery'), ('internal', 'Internal Transfer')],
                                            'Tipo de Operación', related='picking_id.picking_type_id.code')

    @api.model
    def create(self, vals):
        if 'purchase_line_id' in vals and not 'sale_line_id' in vals:
            purchase_line_id = self.env['purchase.order.line'].search([('id', '=', vals['purchase_line_id'])])
            if purchase_line_id.sale_line_id:
                vals['sale_line_id'] = purchase_line_id.sale_line_id.id
        result = super(StockMove, self).create(vals)
        return result

    # @api.depends('sale_line_id')
    @api.depends('purchase_line_id')
    def _compute_palet_type(self):
        for item in self:
            if item.tipouom:
                if 'EUR' in item.tipouom.name or 'GREENBOX' in item.tipouom.name:
                    item.write({'paleteur': item.cantidadpedido})
                    item.write({'paletgr': 0})
                if 'Grande' in item.tipouom.name:
                    item.write({'paletgr': item.cantidadpedido})
                    item.write({'paleteur': 0})
            else:
                item.write({'paletgr': 0, 'paleteur': 0})

    def _set_product_qty(self):
        raise ValidationError('Inverse de product_qty para stock.move')



class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    product_qty = fields.Float('Cantidad', digits=dp.get_precision('Product Unit of Measure'), store=True, copy=False)

    def _set_product_qty(self):
        raise ValidationError('Inverse de product_qty para stock.move.line')
