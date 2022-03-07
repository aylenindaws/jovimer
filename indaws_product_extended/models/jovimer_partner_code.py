# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)


class JovimerPartnerCode(models.Model):
    _name = 'jovimer.partner.code'
    _description = 'Jovimer Partner Code'

    name = fields.Char('Codigo de Cliente')
    partner_id = fields.Many2one('res.partner', string='Cliente')
    product_id = fields.Many2one('product.product', string='Producto')
    label_templates = fields.Many2one('jovimer.etiquetas.plantilla', string='P. Etiquetas', store=True, copy=True,
                                      ondelete='set null')