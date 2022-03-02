# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)


class ModelUom(models.Model):
    _name = 'jovimer.palet'
    _description = 'jovimer palet'

    name = fields.Char('Tipo de Palet')