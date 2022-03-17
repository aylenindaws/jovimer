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

    paleteur = fields.Float(string='Eur')
    paletgr = fields.Float(string='Gr')
    totalbultos = fields.Float(string='Total Bultos')
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