# -*- coding: utf-8 -*-

from odoo import models, fields, api

class preciospedidos(models.Model):
    _inherit = 'stock.inventory.line'

    list_precio = fields.Float(related="product_id.product_tmpl_id.list_price",string="Precios de venta")
    standard_precio = fields.Float(related="product_id.product_tmpl_id.standard_price", string="Precio de compra")
    
    """# --------------------- Campo calculado Venta -------------------------

    def _calc_inventory_value3(self, cr, uid, ids, name, attr, context=None):

        context = dict(context or {})

        res = {}

        uid_company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id

        for quant in self.browse(cr, uid, ids, context=context):

            context.pop('force_company', None)

            if quant.company_id.id != uid_company_id:

                #if the company of the quant is different than the current user company, force the company in the context

                #then re-do a browse to read the property fields for the good company.

                context['force_company'] = quant.company_id.id

                quant = self.browse(cr, uid, quant.id, context=context)

            res[quant.id] = self._get_inventory_value3(cr, uid, quant, context=context)

        return res


    def _get_inventory_value3(self, cr, uid, ids, name, attr, context=None):

        return quant.list_precio * quant.product_qty

    # --------------------- Campo calculado Compra -------------------------

    def _calc_inventory_value2(self, cr, uid, ids, name, attr, context=None):

        context = dict(context or {})

        res = {}

        uid_company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id

        for quant in self.browse(cr, uid, ids, context=context):

            context.pop('force_company', None)

            if quant.company_id.id != uid_company_id:

                #if the company of the quant is different than the current user company, force the company in the context

                #then re-do a browse to read the property fields for the good company.

                context['force_company'] = quant.company_id.id

                quant = self.browse(cr, uid, quant.id, context=context)

            res[quant.id] = self._get_inventory_value2(cr, uid, quant, context=context)

        return res

    def _get_inventory_value2(self, cr, uid, quant, context=None):

        return quant.standard_precio * quant.product_qty

    # --------------------- Columnas -------------------------
    inventory_value3 = fields.Float(compute='_calc_inventory_value3', string="Valoración Venta", readonly=True)
    inventory_value2 = fields.Float(compute='_calc_inventory_value2', string="Valoracion Compra", readonly=True)

    """