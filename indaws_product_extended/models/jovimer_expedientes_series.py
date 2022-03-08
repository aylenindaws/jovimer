# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)

class JovimerExpedientes(models.Model):
    _name = 'jovimer.expedientes.series'
    _description = 'Expedientes Series'
    _order = "name asc"

    name = fields.Char(string='Nombre', help='Nombre Serie')
    partner_id = fields.Many2one('res.partner', string='Cliente', help='Cliente Por defecto')