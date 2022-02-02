# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import datetime


class Schedule_Test(models.Model):
    _name = "schedule.test"
    _description = "Schedule Run History"

    name = fields.Char(string='Name')
    run_date = fields.Datetime('Execute Time')
    count_product = fields.Integer(string='Product Count')
    all_product_list = fields.Text('List of products')