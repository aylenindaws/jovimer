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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    trasnportista = fields.Boolean(string='Transportista')
    #transport_cost = fields.Float('Transport / kg cost')