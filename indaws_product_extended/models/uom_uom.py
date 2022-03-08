# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)


class ModelUom(models.Model):
    _inherit = 'uom.uom'

    # Campos
    invisible = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO')], string='Invisible', default='NO')
    invisiblecp = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO')], string='Cantidad Palets', default='NO')
    invisibleudvta = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO')], string='Unidad de Venta', default='NO')
    invisibleasig = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO')], string='Unidad Asignacion', default='NO')
    nameeng = fields.Char(string='Eng Name')
    pesobruto = fields.Float(string='Peso Bruto')
