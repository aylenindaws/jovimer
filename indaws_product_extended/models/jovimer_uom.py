# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)


class ModelUom(models.Model):
    _inherit = 'uom.uom'
    _name = 'jovimer.uom'