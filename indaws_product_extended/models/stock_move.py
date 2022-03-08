# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    supplier_id = fields.Many2one('res.partner', string="Proveedor")
    stock_check = fields.Boolean("Stock", default=False)