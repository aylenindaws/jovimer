# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)

class JovimerEtiquetas(models.Model):
    _name = 'jovimer.etiquetas'
    _description = 'jovimer etiquetas'

    name = fields.Char(string='Nombre de la Etiqueta')
    content = fields.Text(string='Contenido Etiqueta TXT BULTO')
    content_uom = fields.Text(string='Contenido Etiqueta TXT UNIDAD')
    content_html = fields.Html(string='Contenido Etiqueta HTML')
    order_line_id = fields.Many2one('sale.order.line', string='Linea de Venta')
    order_id = fields.Many2one('sale.order', string='Pedido de Venta', related='order_line_id.order_id', store=True)
    purchase_line_id = fields.Many2one('purchase.order.line', string='Linea de Compra')
    purchase_id = fields.Many2one('purchase.order', string='Pedido de Compra', related='purchase_line_id.order_id', store=True)
    dossier_id = fields.Many2one('jovimer.expedientes', string='Expediente')
    dossier_campaign = fields.Selection(related='dossier_id.campanya')
    dossier_series_id = fields.Many2one('jovimer.expedientes.series', related='dossier_id.serie')
    dossier_num = fields.Integer('Numero de Serie', related='dossier_id.name')
    label_template_id = fields.Many2one('jovimer.etiquetas.plantilla', string='Plantilla')
    partner_id = fields.Many2one('res.partner', string='Proveedor')
    partner_code = fields.Char(string='Codigo Cliente')