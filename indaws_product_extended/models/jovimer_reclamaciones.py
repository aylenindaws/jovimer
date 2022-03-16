# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)


class JovimerReclamaciones(models.Model):
    _name = 'jovimer.reclamaciones'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'jovimer reclamaciones'

    name = fields.Char(string='Codigo Reclamacion')
    asunto = fields.Char(string='Tema Reclamacion')
    fechasaalta = fields.Date(string='Fecha de Alta')
    fechabaja = fields.Date(string='Fecha de Baja')
    campanya = fields.Char(string='Serie / Campaña', help='Número Expediente')
    expediente = fields.Many2one('account.analytic.account', string='Expediente')
    cliente = fields.Many2one('res.partner', string='Proveedor reclamación')
    lineaspedido = fields.Many2many('sale.order', string='Documentos de Venta Afectados')
    detalledocumentos = fields.Many2many('sale.order.line', string='Lineas de Documentos Afectadas')
    detalledocumentoscompra = fields.Many2many('purchase.order.line', string='Lineas de Documentos de Compra Afectados')
    detalledocumentoscontables = fields.Many2many('account.move.line',string='Lineas de Documentos Contables Afectados')
    observacionescliente = fields.Text(string='Observaciones Cliente')
    observacionescliente = fields.Text(string='Observaciones Cliente')
    imagenes = fields.One2many('jovimer.imagenes.reclamaciones', 'reclamacion', string='Imágenes Reclacionadas')
    accionescorrectivas = fields.Text(string='Acciones Correctivas')
    status = fields.Selection([
        ('ABIERTA', 'ABIERTA'),
        ('EN CURSO', 'EN CURSO'),
        ('CERRADA', 'CERRADA'),
        ('CANCELADA', 'CANCELADA'),
        ('DESESTIMADA', 'DESESTIMADA'),
    ], string='Estado', default='ABIERTA')

class ModelReclamacionesImagenes(models.Model):
    # Tabla Reclamaciones
    _name = 'jovimer.imagenes.reclamaciones'

    # Campos Pesonalizados en pedidos de Venta
    name = fields.Char(string='Codigo Reclamacion')
    imagen = fields.Binary(string='Imagen Reclamacion')
    reclamacion = fields.Many2one('jovimer.reclamaciones', string='Reclamación')