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