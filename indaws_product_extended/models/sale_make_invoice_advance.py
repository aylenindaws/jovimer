# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)
        invoice_vals['invoice_line_ids'] = [(5, 0, 0)]
        raise ValidationError(so_line)
        invoice_vals['invoice_line_ids'] = [(0, 0, {
            'name': name,
            'price_unit': amount,
            'quantity': 1.0,
            'product_id': self.product_id.id,
            'product_uom_id': so_line.product_uom.id,
            'tax_ids': [(6, 0, so_line.tax_id.ids)],
            'sale_line_ids': [(6, 0, [so_line.id])],
            'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
            'analytic_account_id': order.analytic_account_id.id or False,
        })]
        return invoice_vals