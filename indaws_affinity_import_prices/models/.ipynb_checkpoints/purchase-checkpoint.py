import time
import json
import io
import datetime
import tempfile
import binascii
import xlrd
import itertools
import statistics
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, _, exceptions
from odoo.addons import decimal_precision as dp
import logging
from operator import itemgetter
_logger = logging.getLogger(__name__)

    
    
    
class product_pricelist_load(models.Model):
    _name = 'product.pricelist.load'
    _order = 'date'
    
    date = fields.Date('Date', required=True, default=fields.Date.today())
    validity = fields.Date('Valid until', required=True)
    delivery_time = fields.Integer('Delivery time (days)')
    transport_cost = fields.Float('Transport / kg cost', related="partner_id.transport_cost")
    margin = fields.Float('Margin (%)', related="partner_id.margin")
    not_update_prices = fields.Boolean('No actualizar precios', related="partner_id.not_update_prices")
    file_to_upload = fields.Binary('File')
    partner_id = fields.Many2one('res.partner',string="Supplier", required=True)
    replace = fields.Boolean('Replace pricelist', default=True)
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.user.company_id)
    
    file_line_ids = fields.One2many('product.pricelist.load.line', 'file_load_id',
                                 'Product Price List Lines', readonly=True)
                                 
    
    def find_product(self, product_code):   
        product_ids = self.env['product.product'].search([('default_code', '=', product_code)])
        if product_ids:
            product_id  = product_ids[0]
            return product_id
        else:
            return None
            
    def find_product_template(self, product_code):   
        product_ids = self.env['product.template'].search([('default_code', '=', product_code)])
        if product_ids:
            product_id  = product_ids[0]
            return product_id
        else:
            return None
            
    def find_supplierinfo_template(self, product_id, company_id):   
        product_ids = self.env['product.supplierinfo'].search([('product_tmpl_id', '=', product_id.id), ('company_id', '=', company_id.id), ('name', '=', self.partner_id.id)])
        if product_ids:
            product_id  = product_ids[0]
            return product_id
        else:
            return None
            
    def find_supplierinfo_product(self, product_id, company_id):   
        product_ids = self.env['product.supplierinfo'].search([('product_id', '=', product_id.id), ('company_id', '=', company_id.id), ('name', '=', self.partner_id.id)])
        if product_ids:
            product_id  = product_ids[0]
            return product_id
        else:
            return None
            
            
    def create_supplierinfo(self, line, product_tmpl_id, product_id):
    
        idprod = None
        idtemp = None
        if product_tmpl_id:
            idtemp = product_tmpl_id.id
        if product_id:
            idprod = product_id.id
    
        sup_id = self.env['product.supplierinfo'].create({'name':self.partner_id.id,
                                                           'delay':1,
                                                           'product_tmpl_id':idtemp,
                                                           'product_id':idprod,
                                                           'min_qty':0,
                                                           'price':line.price,
                                                           'date_start':self.date,
                                                           'date_end':self.validity,
                                                           'delay':self.delivery_time,
                                                           'cantidad': line.cantidad,
                                                           #'transport_cost': self.transport_cost,
                                                           #'margin':self.margin,
                                                           'company_id':self.company_id.id,
                                                            }) 
        return sup_id
            
            
    def import_product_lines(self):
        if len(self.file_line_ids) <= 0:
            try:
                fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.file_to_upload))
                fp.seek(0)
                values = {}
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise exceptions.ValidationError(_('Invalid File!!'))
                
            product_obj = self.env['product.product']
            lines = []
            data  = []                
            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))

                    
                    move = self.env['product.pricelist.load.line'].create({'file_load_id':self.id,
                                                                           'code':line[0],
                                                                           'product_name':line[1],
                                                                           'price':line[2],
                                                                           'cantidad':int(float(line[3])),
                                                                           'un_cs':int(float(line[4])),
                                                                           'vol_cl':line[5],
                                                                           'avb':line[6],
                                                                           'nrb':line[7],
                                                                           'procesado':False,
                                                                           'fail':False,
                                                                           'fail_reason':None,
                                                                            }) 
            
            
    def process_all_products(self):
        for product in self.env['product.template'].search([('active', '=', True)]):
            product.actualizar_precios()

    def process_lines(self):
        
        if self.replace == True:
            psupplinfo_lst = self.env['product.supplierinfo'].search([('name', '=', self.partner_id.id)]).unlink()
        
        for line in self.env['product.pricelist.load.line'].search([('file_load_id', '=', self.id),('procesado', '=', False)]):
            error = False
            product_id = self.find_product_template(line.code)
            if product_id:
                supinfo = self.find_supplierinfo_template(product_id, self.company_id)
                if supinfo:
                    supinfo.price = line.price
                else:
                    self.create_supplierinfo(line, product_id, None)
                    
                #Actualizamos precio
                if self.partner_id.not_update_prices == False:
                    product_id.actualizar_precios()
            
            else:
                product_id = self.find_product(line.code)
                if product_id:
                    supinfo = self.find_supplierinfo_product(product_id, self.company_id)
                    if supinfo:
                        supinfo.price = line.price
                    else:
                        self.create_supplierinfo(line, product_id.product_tmpl_id, product_id)
                        
                    
                        
                else:
                    line.procesado = False
                    line.fail = True
                    line.fail_reason = 'PRODUCTO NO ENCONTRADO'
                    error = True
            
            if error == False:
                line.procesado = True
                line.fail = False

         
        

    
class product_pricelist_load_line(models.Model):
    _name = 'product.pricelist.load.line'
    
    code = fields.Char('Product Code', required=True)
    product_name = fields.Char('Product Name', required=True)
    price = fields.Float('Product Price', required=True)
    cantidad = fields.Float('Quantity', required=True)
    un_cs = fields.Integer('UN x CS')
    vol_cl = fields.Float('Vol CL')
    avb = fields.Float('AVB %')
    nrb = fields.Char('NRB')
    
    
    procesado = fields.Boolean('Processed', default=False)
    fail = fields.Boolean('Fail')
    fail_reason = fields.Char('Fail Reason')
    file_load_id = fields.Many2one('product.pricelist.load', 'Load',
                                required=True, ondelete='cascade')
    
    

    
class res_partner(models.Model):
    _inherit = 'res.partner'
    
    transport_cost = fields.Float('Transport / kg cost')
    margin = fields.Float('Margin (%)')
    not_update_prices = fields.Boolean('No actualizar precios')
    
    
    
class product_supplierinfo(models.Model):
    _inherit = 'product.supplierinfo'
    
    transport_cost = fields.Float('Transport / kg cost', related="name.transport_cost")
    margin = fields.Float('Margin (%)', related="name.margin")
    not_update_prices = fields.Boolean('No actualizar precios', related="name.not_update_prices")
    cantidad = fields.Float('Stock supplier')
    
    price_entregado = fields.Float(compute="_value_prices_product", string="Precio entregado")
    price_sale_recommend = fields.Float(compute="_value_prices_product", string="Precio recomendado")
    

    @api.depends('margin', 'transport_cost', 'price', 'product_id.weight', 'product_tmpl_id.weight')
    def _value_prices_product(self):
        for record in self:
            price_entregado = 0.0
            price_sale_recommend = 0.0
            weight = 0.0
            if record.product_id:
                if record.product_id.weight > 0:
                    weight = record.product_id.weight
            if weight <= 0.0:
                if record.product_tmpl_id:
                    if record.product_tmpl_id.weight > 0:
                        weight = record.product_tmpl_id.weight
            
            record.price_entregado = record.price + ( record.transport_cost * weight)
            record.price_sale_recommend = 0.0
            if record.margin < 100:
                record.price_sale_recommend = record.price_entregado / (1 - record.margin / 100)
    
    
    inc_cost = fields.Float(digits=(6, 2), string='Cost increase (%)', compute='_calculate_cost_increase')
    product_code = fields.Char(string='Product code', compute='_calculate_cost_increase')
    min_supplier_id = fields.Many2one('res.partner', string='Min cost supplier', compute='_calculate_cost_increase', readonly=True)
    min_cost = fields.Float(digits=(6, 2), string='Min cost', compute='_calculate_cost_increase')
    average_cost = fields.Float(digits=(8, 4), string="Average cost", compute='_calculate_cost_increase', readonly=True)
    median_cost = fields.Float(digits=(8, 4), string="Median cost", compute='_calculate_cost_increase', readonly=True)
    variation_median_cost = fields.Float(digits=(8, 4), string="Variation Median cost (%)", compute='_calculate_cost_increase', readonly=True)
    date_min_cost = fields.Date(string="Fecha precio", compute='_calculate_cost_increase', readonly=True)
    
    @api.depends('product_tmpl_id')
    def _calculate_cost_increase(self):
        for record in self:
            price = 0.0
            inc = 0.0
            
            if record.product_tmpl_id:
                record.product_code = record.product_tmpl_id.default_code
                record.min_cost = record.product_tmpl_id.min_cost
                record.date_min_cost = record.product_tmpl_id.date_min_cost
                record.median_cost = record.product_tmpl_id.median_cost
                record.average_cost = record.product_tmpl_id.average_cost
                record.min_supplier_id = None
                if record.product_tmpl_id.min_supplier_id:
                    record.min_supplier_id = record.product_tmpl_id.min_supplier_id.id
                    
                #calculo incremento
                dif = record.price_entregado - record.median_cost
                variation_median_cost = 0.0
                if record.median_cost > 0:
                    variation_median_cost = (dif / record.median_cost) * 100
                record.variation_median_cost = variation_median_cost
            


            price = record.price_entregado
            if record.product_tmpl_id.min_cost > 0.0:
                if price > record.product_tmpl_id.min_cost:
                    inc = ((price - record.product_tmpl_id.min_cost) / record.product_tmpl_id.min_cost) * 100
            record.inc_cost = inc
            
            


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
            num_prices = 0
            min_supplier_delay = 0
            min_supplier_cantidad = 0
            
            lista_costes = []
            
            for sup in record.seller_ids:
                lista_costes.append(sup.price_entregado)
                sum = sum + sup.price_entregado
                count = count + 1
                if sup.price_entregado < min_cost and sup.price > 0.0 and sup.cantidad > 0:
                    min_cost = sup.price_entregado
                    sup_id = sup.name.id
                    date_min_cost = sup.create_date
                    min_supplier_delay = sup.delay
                    min_supplier_cantidad = sup.cantidad
                if min_cost == 0.0 and sup.price > 0.0 and sup.cantidad > 0:
                    min_cost = sup.price_entregado
                    sup_id = sup.name.id
                    date_min_cost = sup.create_date
                    min_supplier_delay = sup.delay
                    min_supplier_cantidad = sup.cantidad
            
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
            record.min_supplier_delay = min_supplier_delay
            record.min_supplier_cantidad = min_supplier_cantidad
