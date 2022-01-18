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