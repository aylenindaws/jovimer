# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)

class JovimerMarca(models.Model):
    _name = 'jovimer.marca'
    _description = 'jovimer marca'

    name = fields.Char('Nombre')
    code = fields.Char(string='Código')
    abrev = fields.Char(string='abrev')
    print_name = fields.Char(string='Impresión')
    import_velneo = fields.Boolean(string='Importado Velneo')