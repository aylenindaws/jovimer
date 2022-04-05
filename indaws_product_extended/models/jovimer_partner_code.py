# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)


class JovimerPartnerCode(models.Model):
    _name = 'jovimer.partner.code'
    _description = 'Jovimer Partner Code'

    name = fields.Char('Codigo de Cliente')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Cliente')
    template_id = fields.Many2one(comodel_name='product.template', string='Producto')
    label_templates = fields.Many2one(comodel_name='jovimer.etiquetas.plantilla', string='P. Etiquetas', copy=True, ondelete='set null')