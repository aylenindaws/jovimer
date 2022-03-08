# -*- coding: utf-8 -*-
import base64
import os.path

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, time, timedelta
import subprocess
import logging
import datetime

_logger = logging.getLogger(__name__)


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    transport_cost = fields.Float('Transport / kg cost', related="name.transport_cost")
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=lambda self: self.product_id.default_supplierinfo_discount)