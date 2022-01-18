# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)

class JovimerCalibre(models.Model):
    _name = 'jovimer.calibre'
    _description = 'jovimer calibre'

    name = fields.Char('Nombre')
    