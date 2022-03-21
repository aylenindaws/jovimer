# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
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

    @api.depends('sale_line_id')
    def _compute_palet_type(self):
        for item in self:
            if item.sale_line_id:
                if 'EUR' in item.sale_line_id.tipouom.name or 'GREENBOX' in item.sale_line_id.tipouom.name:
                    item.write({'paleteur': item.sale_line_id.cantidadpedido})
                    item.write({'paletgr': 0})
                if 'Grande' in item.sale_line_id.tipouom.name:
                    item.write({'paletgr': item.sale_line_id.cantidadpedido})
                    item.write({'paleteur': 0})
                item.totalbultos = item.sale_line_id.bultos