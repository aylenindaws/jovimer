# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)

class JovimerPlataforma(models.Model):
    _name = 'jovimer.plataforma'
    _description = 'jovimer plataforma'

    name = fields.Char('Plataforma')
    partner_id = fields.Many2one('res.partner', string='Cliente')