# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)

class JovimerConflote(models.Model):
    _name = 'jovimer.conflote'
    _description = 'jovimer conflote'

    name = fields.Char('Nombre')
    display_name = fields.Char(string='Display Name', readonly=True)
    code = fields.Char(string='Código')
    formula = fields.Char(string='Formula')
