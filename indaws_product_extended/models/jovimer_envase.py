# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)

class JovimerEnvase(models.Model):
    _name = 'jovimer.envase'
    _description = 'jovimer envase'

    name = fields.Char('Nombre')