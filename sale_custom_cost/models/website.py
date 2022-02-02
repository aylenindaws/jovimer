# -*- coding: utf-8 -*-
from odoo import models


class Website(models.Model):
    _inherit = 'website'

    def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
        res = super(Website, self).sale_get_order(force_create=force_create, code=code, update_pricelist=update_pricelist, force_pricelist=force_pricelist)
        for record in res.order_line:
            record._onchange_product_id()
            record._onchange_product_id_cost_real()
        return res