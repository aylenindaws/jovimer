# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)

class JovimerConfeccion(models.Model):
    _name = 'jovimer.confeccion'
    _description = 'jovimer confeccion'

    name = fields.Char('Nombre')
    code = fields.Char(string='Código')
    abr = fields.Char(string='abrev')
    import_name = fields.Char(string='Nombre Importado')
    import_velneo = fields.Boolean(string='Importado Velneo')
    bulge_euro_palet = fields.Float(string='Bultos Euro Palet')
    bulge_grand_palet = fields.Float(string='Bultos Palet Grande')
    kg_net_bulge = fields.Float(string='KG/NET Bulto')
    uom_for_bulge = fields.Float(string='Unidad por Bulto')
    print_name = fields.Char(string='Impresion')
    tara = fields.Float(string='Tara')
    uom_bulto = fields.Many2one('uom.uom', string='Tipo Cálculo / Ud Venta', domain=[('invisible', '=', 'NO')])
    template_id = fields.One2many('product.template', 'confeccion', string='Plantillas Afectadas')