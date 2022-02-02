# -*- coding: utf-8 -*-

import statistics
from datetime import datetime, date
from odoo import models, fields, api, _
import logging
from dateutil import relativedelta

_logger = logging.getLogger(__name__)



class product_template(models.Model):
    _inherit = 'product.template'

    average_cost = fields.Float(digits=(8, 4), string="Average cost", compute='_get_supplier_costs', readonly=True)
    median_cost = fields.Float(digits=(8, 4), string="Median cost", compute='_get_supplier_costs', readonly=True)
    min_cost = fields.Float(digits=(8, 4), string="Min cost", compute='_get_supplier_costs', readonly=True)
    date_min_cost = fields.Date(string="Fecha precio", compute='_get_supplier_costs', readonly=True)
    min_supplier_id = fields.Many2one('res.partner', string='Min cost supplier', compute='_get_supplier_costs', readonly=True)
    num_prices = fields.Integer(string="Num prices", compute='_get_supplier_costs', readonly=True)
    min_supplier_delay = fields.Integer(string="Delay", compute='_get_supplier_costs', readonly=True)
    min_supplier_cantidad = fields.Integer(string="Stock proveedor", compute='_get_supplier_costs', readonly=True)
    fixed_price = fields.Float(string="Fixed price")
    stock_available_website = fields.Text(string="Stock Available Website", compute="_compute_stock_available_website")
    variation_median_cost = fields.Float(string="Variation Median Cost", compute='_get_supplier_costs', readonly=True)
    code_vendor_ids = fields.One2many('vendor.product.code', 'product_tmpl_id', 'Code Proveedor')
    date_end_supplier = fields.Date(string="Fecha Final", compute='_get_supplier_costs', readonly=True)
    date_start_supplier = fields.Date(string="Fecha Final", compute='_get_supplier_costs', readonly=True)


    def _compute_stock_available_website(self):
        stock_move_obj = self.env['stock.move']
        today = fields.Date.today()
        warehouse = self.env['stock.warehouse'].search([('company_id', 'in', self.env.context.get('allowed_company_ids', False))])
        for record in self.with_context(warehouse=warehouse.ids):
            moves = stock_move_obj.search([('product_id.product_tmpl_id', '=', record.id), ('state', '=', 'assigned'),
                                           ('company_id', 'in', self.env.context.get('allowed_company_ids', False)),
                                           ('picking_code', '=', 'incoming')], order='date_deadline asc')
            record.stock_available_website = ''
            if record.qty_available > 0 and record.incoming_qty == 0:
                if record.virtual_available <= 0:
                    record.stock_available_website = ''
                else:
                    record.stock_available_website += str(int(record.virtual_available)) + ' En Stock' + '\n'
            elif record.qty_available > 0 and record.incoming_qty > 0:
                if record.virtual_available > record.incoming_qty:
                    if record.virtual_available <= 0:
                        record.stock_available_website = ''
                    else:
                        record.stock_available_website += str(int(record.virtual_available - record.incoming_qty)) + ' En Stock' + '\n'
                        for move in moves:
                            if move and move.purchase_line_id and move.purchase_line_id.order_id and move.purchase_line_id.order_id.date_planned:
                                record.stock_available_website += str(int(move.product_uom_qty)) + ' ' + record.uom_id.name + ' Disponible: ' + str(move.purchase_line_id.order_id.date_planned.date().strftime("%d/%m")) + '\n'
                elif record.virtual_available < record.incoming_qty:
                    if record.virtual_available <= 0:
                        record.stock_available_website = ''
                    else:
                        if len(moves) == 1:
                            for move in moves:
                                if record.virtual_available <= move.product_uom_qty:
                                    if move and move.purchase_line_id and move.purchase_line_id.order_id and move.purchase_line_id.order_id.date_planned:
                                        record.stock_available_website += str(
                                            int(record.virtual_available)) + ' ' + record.uom_id.name + ' Disponible: ' + str(move.purchase_line_id.order_id.date_planned.date().strftime("%d/%m")) + '\n'
                        elif len(moves) > 1:
                            qty = record.virtual_available
                            for move in moves:
                                if qty > 0:
                                    if qty >= move.product_uom_qty:
                                        if move and move.purchase_line_id and move.purchase_line_id.order_id and move.purchase_line_id.order_id.date_planned:
                                            record.stock_available_website += str(int(move.product_uom_qty)) + ' ' + record.uom_id.name + ' Disponible: ' + str(move.purchase_line_id.order_id.date_planned.date().strftime("%d/%m")) + '\n'
                                        qty -= move.product_uom_qty
                                    elif qty < move.product_uom_qty:
                                        if move and move.purchase_line_id and move.purchase_line_id.order_id and move.purchase_line_id.order_id.date_planned:
                                            record.stock_available_website += str(int(qty)) + ' ' + record.uom_id.name + ' Disponible: ' + str(move.purchase_line_id.order_id.date_planned.date().strftime("%d/%m")) + '\n'
                                        qty -= move.product_uom_qty
                else:
                    record.stock_available_website = ''
                    if record.virtual_available != 0:
                        for move in moves:
                            if move and move.purchase_line_id and move.purchase_line_id.order_id and move.purchase_line_id.order_id.date_planned:
                                record.stock_available_website += str(int(move.product_uom_qty)) + ' ' + record.uom_id.name + ' Disponible: ' + str(move.purchase_line_id.order_id.date_planned.date().strftime("%d/%m")) + '\n'

            elif not record.qty_available and not record.incoming_qty:
                # Added condition for minus value of field.
                if record.virtual_available < 0:
                    qty = int(record.min_supplier_cantidad + record.virtual_available)
                    if qty > 0 and (today >= record.date_start_supplier and today <= record.date_end_supplier):
                        delivery_date = today + relativedelta.relativedelta(days=record.min_supplier_delay)
                        record.stock_available_website = str(qty) + ' ' + record.uom_id.name + ' Disponible: ' + delivery_date.strftime("%d/%m") + '\n'
                    else:
                        record.stock_available_website = ''
                elif record.virtual_available == 0 and record.min_supplier_cantidad > 0:
                    if today >= record.date_start_supplier and today <= record.date_end_supplier:
                        delivery_date = today + relativedelta.relativedelta(days=record.min_supplier_delay)
                        record.stock_available_website += str(int(record.min_supplier_cantidad + record.virtual_available)) + ' ' + record.uom_id.name + ' Disponible: ' + delivery_date.strftime("%d/%m") + '\n'
                    else:
                        record.stock_available_website = ''
                else:
                    record.stock_available_website = ''
            # Condition added to update stock_available_website field when forecasted updated and Onhand is 0
            elif not record.qty_available and record.virtual_available > 0:
                for move in moves:
                    if move and move.purchase_line_id and move.purchase_line_id.order_id and move.purchase_line_id.order_id.date_planned:
                        if move and move.purchase_line_id and move.purchase_line_id.order_id and move.purchase_line_id.order_id.date_planned:
                            record.stock_available_website = str(int(record.virtual_available)) + ' ' + record.uom_id.name + ' Disponible: ' + str(move.purchase_line_id.order_id.date_planned.date().strftime("%d/%m")) + '\n'

    def cron_published_schedule(self):
        """schedule action run every 1 day"""
        product = self.env['product.template'].search([])
        count_product = 0
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)])
        for record in product.with_context(warehouse=warehouse.ids):
            count_product += 1
            if record.list_price > 0 and record.stock_available_website != "":
                record.write({'is_published': True})
            else:
                record.write({'is_published': False})

            # Group 2
            # date_stocks_avaliable for sort by second block
            stock_move_obj = self.env['stock.move']
            today = fields.Date.today()
            record.write({'date_stocks_avaliable': False})
            moves = stock_move_obj.search([
                ('product_id.product_tmpl_id', '=', record.id), ('state', '=', 'assigned'),
                ('picking_code', '=', 'incoming'), ('company_id', '=', self.env.user.company_id.id)
            ], order='date_deadline asc')

            if record.stock_available_website:
                if record.qty_available > 0 and record.incoming_qty > 0:
                    if record.virtual_available > record.incoming_qty:
                        if record.virtual_available <= 0:
                            record.write({'date_stocks_avaliable': False})
                        else:
                            if moves:
                                if moves[0].purchase_line_id and moves[0].purchase_line_id.order_id and moves[0].purchase_line_id.order_id.date_planned:
                                    record.date_stocks_avaliable = moves[0].purchase_line_id.order_id.date_planned.date().strftime("%Y-%m-%d")
                    elif record.virtual_available < record.incoming_qty:
                        if record.virtual_available <= 0:
                            record.write({'date_stocks_avaliable': False})
                        else:
                            if len(moves) == 1:
                                if record.virtual_available <= moves[0].product_uom_qty :
                                    if moves[0].purchase_line_id and moves[0].purchase_line_id.order_id and moves[0].purchase_line_id.order_id.date_planned:
                                        record.date_stocks_avaliable = moves[0].purchase_line_id.order_id.date_planned.date().strftime("%Y-%m-%d")
                            elif len(moves) > 1:
                                qty = record.virtual_available
                                if qty > 0:
                                    if qty >= moves[0].product_uom_qty:
                                        if moves[0].purchase_line_id and moves[0].purchase_line_id.order_id and moves[0].purchase_line_id.order_id.date_planned:
                                            record.date_stocks_avaliable = moves[0].purchase_line_id.order_id.date_planned.date().strftime("%Y-%m-%d")
                                        qty -= moves[0].product_uom_qty
                                    elif qty < moves[0].product_uom_qty:
                                        if moves[0].purchase_line_id and moves[0].purchase_line_id.order_id and moves[0].purchase_line_id.order_id.date_planned:
                                            record.date_stocks_avaliable = moves[0].purchase_line_id.order_id.date_planned.date().strftime("%Y-%m-%d")
                                        qty -= moves[0].product_uom_qty
                    else:
                        if record.virtual_available != 0:
                            if moves:
                                if moves[0].purchase_line_id and moves[0].purchase_line_id.order_id and moves[0].purchase_line_id.order_id.date_planned:
                                    record.date_stocks_avaliable = moves[0].purchase_line_id.order_id.date_planned.date().strftime("%Y-%m-%d")
                elif not record.qty_available and record.virtual_available > 0:
                    if moves:
                        if moves[0].purchase_line_id and moves[0].purchase_line_id.order_id and moves[0].purchase_line_id.order_id.date_planned:
                            record.date_stocks_avaliable = moves[-1].purchase_line_id.order_id.date_planned.date().strftime("%Y-%m-%d")
                else:
                    if record.virtual_available != 0:
                        if moves:
                            if moves[0].purchase_line_id and moves[0].purchase_line_id.order_id and moves[0].purchase_line_id.order_id.date_planned:
                                record.date_stocks_avaliable = moves[-1].purchase_line_id.order_id.date_planned.date().strftime("%Y-%m-%d")

                # Group 3
                # deliverys_date for sort by third block
                record.write({'deliverys_date': False})
                if not record.qty_available and not record.incoming_qty:
                    if record.virtual_available < 0:
                        record.write({'deliverys_date': False})
                    elif record.min_supplier_cantidad:
                        delivery_date = today + relativedelta.relativedelta(days=record.min_supplier_delay)
                        record.deliverys_date = delivery_date.strftime("%Y-%m-%d")
                    else:
                        record.write({'deliverys_date': False})
        vals = {
            'name': 'Product Published',
            'run_date': datetime.now(),
            'count_product': count_product,
            'all_product_list': product
        }
        s_test = self.env['schedule.test'].create(vals)


    def check_product_e_commerce_category_schedule(self):
        """schedule action run every 1 day"""
        label = self.env['product.label.line'].search([('label', 'in', [item.id for item in self.env['product.label'].search([('name', '=', 'Vendido')])])])
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)])
        for record in label:
            product = record.product_tmpl_id.with_context(warehouse=warehouse.ids)
            product_qty = 0 if product.stock_available_website == '' else float(product.stock_available_website.split(' ')[0])
            if product_qty >= 0:
                record.unlink()
        categ = self.env['product.public.category'].search([('name','=','OFERTAS ESPECIALES')])
        product = self.env['product.template'].search([('public_categ_ids','in',categ.id)])
        for record in product.with_context(warehouse=warehouse.ids):
            product_qty = 0 if record.stock_available_website == '' else float(record.stock_available_website.split(' ')[0])
            if product_qty <= 0:
                record.write({"public_categ_ids": [(3, categ.id)]})

    @api.onchange('fixed_price')
    def _onchange_fixed_price(self):
        self.list_price = self.fixed_price

    def actualizar_precios(self):
        for record in self:
            if record.fixed_price > 0.0:
                record.list_price = record.fixed_price
            else:
                hay_precio = False
                for linprov in record.seller_ids:
                    if linprov.date_end and fields.Date.today() <= linprov.date_end and linprov.name.not_update_prices == False and linprov.cantidad > 0:
                        if hay_precio == False:
                            hay_precio = True
                            precio = linprov.price_sale_recommend
                        else:
                            if linprov.price_sale_recommend < precio:
                                precio = linprov.price_sale_recommend
                if hay_precio == True:
                    record.list_price = precio

    @api.depends('seller_ids')
    def _get_supplier_costs(self):
        for record in self:
            min_cost = 0.0
            sum = 0
            count = 0
            sup_id = None
            date_min_cost = None
            variation_median_cost = 0
            min_supplier_delay = 0
            min_supplier_cantidad = 0
            today = fields.Date.today()
            date_end_supplier = None
            date_start_supplier = None
            lista_costes = []

            for sup in record.seller_ids:
                lista_costes.append(sup.price_entregado)
                sum = sum + sup.price_entregado
                count = count + 1
                if sup.price_entregado < min_cost and sup.price > 0.0 and sup.cantidad > 0 and sup.name.not_update_prices == False and sup.date_end >= today:
                    min_cost = sup.price_entregado
                    sup_id = sup.name.id
                    variation_median_cost = sup.variation_median_cost
                    date_min_cost = sup.create_date
                    min_supplier_delay = sup.delay
                    min_supplier_cantidad = sup.cantidad
                    date_end_supplier = sup.date_end
                    date_start_supplier = sup.date_start

                if min_cost == 0.0 and sup.price > 0.0 and sup.cantidad > 0 and sup.name.not_update_prices == False and sup.date_end >= today:
                    min_cost = sup.price_entregado
                    sup_id = sup.name.id
                    variation_median_cost = sup.variation_median_cost
                    date_min_cost = sup.create_date
                    min_supplier_delay = sup.delay
                    min_supplier_cantidad = sup.cantidad
                    date_end_supplier = sup.date_end
                    date_start_supplier = sup.date_start

            average_cost = 0.0
            if count > 0.0:
                average_cost = sum / count

            median_cost = 0.0
            if len(lista_costes) > 0:
                median_cost = statistics.median(lista_costes)

            record.min_cost = min_cost
            record.average_cost = average_cost
            record.min_supplier_id = sup_id
            record.date_min_cost = date_min_cost
            record.median_cost = median_cost
            record.num_prices = len(lista_costes)
            record.variation_median_cost = variation_median_cost
            record.min_supplier_delay = min_supplier_delay
            record.min_supplier_cantidad = min_supplier_cantidad
            record.date_end_supplier = date_end_supplier
            record.date_start_supplier = date_start_supplier
