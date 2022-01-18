# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)

class JovimerCategoria(models.Model):
    _name = 'jovimer.categoria'
    _description = 'jovimer categoria'

    name = fields.Char('Nombre')