# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)

class JovimerEtiquetasPlantilla(models.Model):
    _name = 'jovimer.etiquetas.plantilla'
    _description = 'jovimer etiquetas plantilla'

    name = fields.Char('Nombre')
    content = fields.Text(string='Contenido Etiqueta TXT')
    content_uom = fields.Text(string='Contenido Etiqueta TXT UNIDAD')
    lang = fields.Many2one('res.lang', string='Lenguaje', help='Lengua Nativa de la Etiqueta')
    content_html = fields.Html(string='Contenido Etiqueta Enriquecida')
    template_id = fields.One2many('product.template', 'label_templates', string='Plantilla Producto')
    label_id = fields.One2many('jovimer.etiquetas', 'label_template_id', string='Etiquetas')