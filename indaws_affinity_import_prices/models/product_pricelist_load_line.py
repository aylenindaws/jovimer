# -*- coding: utf-8 -*-

from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)



class product_pricelist_load_line(models.Model):
    _name = 'product.pricelist.load.line'

    code = fields.Char('Product Code', required=True)
    product_name = fields.Char('Product Name', required=True)
    price = fields.Float('Product Price', required=True)
    cantidad = fields.Float('Quantity', required=True)
    delivery_time = fields.Integer('Delivery time (days)')
    vendor_code = fields.Char('Vendor Code')
    procesado = fields.Boolean('Processed', default=False)
    fail = fields.Boolean('Fail')
    fail_reason = fields.Char('Fail Reason')
    file_load_id = fields.Many2one('product.pricelist.load', 'Load', required=True, ondelete='cascade')