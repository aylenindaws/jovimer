# -*- coding: utf-8 -*-

import tempfile
import binascii
import xlrd
from odoo import models, fields, _, exceptions
import logging
import xlsxwriter, base64

_logger = logging.getLogger(__name__)


class product_pricelist_load(models.Model):
    _name = 'product.pricelist.load'
    _order = 'date'

    date = fields.Date('Date', required=True, default=fields.Date.today())
    validity = fields.Date('Valid until', required=True)
    transport_cost = fields.Float('Transport / kg cost', related="partner_id.transport_cost")
    margin = fields.Float('Margin (%)', related="partner_id.margin")
    not_update_prices = fields.Boolean('No actualizar precios', related="partner_id.not_update_prices")
    file_to_upload = fields.Binary('File')
    partner_id = fields.Many2one('res.partner', string="Supplier", required=True)
    replace = fields.Boolean('Replace pricelist', default=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)
    file_line_ids = fields.One2many('product.pricelist.load.line', 'file_load_id', 'Product Price List Lines', readonly=True)
    file = fields.Binary('File Errors')
    view_list_error = fields.Boolean('view_list_error', default=False)

    def find_product(self, product_code):
        product_ids = self.env['product.product'].search([('default_code', '=', product_code)])
        if product_ids:
            product_id = product_ids[0]
            return product_id
        else:
            return None

    def find_product_template(self, product_code):
        product_ids = self.env['product.template'].search([('default_code', '=', product_code)])
        if product_ids:
            product_id = product_ids[0]
            return product_id
        else:
            return None

    def find_supplierinfo_template(self, product_id, company_id, partner_id):
        product_ids = self.env['product.supplierinfo'].search([('product_tmpl_id', '=', product_id.id), ('company_id', '=', company_id.id), ('name', '=', partner_id.id)])
        if product_ids:
            product_id = product_ids[0]
            return product_id
        else:
            return None

    def find_supplierinfo_product(self, product_id, company_id):
        product_ids = self.env['product.supplierinfo'].search([('product_id', '=', product_id.id), ('company_id', '=', company_id.id), ('name', '=', self.partner_id.id)])
        if product_ids:
            product_id = product_ids[0]
            return product_id
        else:
            return None

    def create_supplierinfo(self, line, product_tmpl_id, product_id, partner_id):
        idprod = None
        idtemp = None
        if product_tmpl_id:
            idtemp = product_tmpl_id.id
        if product_id:
            idprod = product_id.id

        sup_id = self.env['product.supplierinfo'].create({'name': partner_id.id,
                                                          'product_tmpl_id': idtemp,
                                                          'product_id': idprod,
                                                          'min_qty': 0,
                                                          'price': line.price,
                                                          'date_start': self.date,
                                                          'date_end': self.validity,
                                                          'delay': line.delivery_time,
                                                          'cantidad': line.cantidad,
                                                          'company_id': self.company_id.id,
                                                          })
        return sup_id

    def import_product_lines(self):
        if len(self.file_line_ids) <= 0:
            try:
                fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.file_to_upload))
                fp.seek(0)
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise exceptions.ValidationError(_('Invalid File!!'))

            data_line = []
            cont = 0
            for row_no in range(sheet.nrows):
                if row_no <= 0:
                    fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    line = list(map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    if (line[0] != '' or line[1] != '') and line[3] != '' and line[4] != '' and line[5] != '':
                        data_line.append({'file_load_id': self.id,
                                           'code': line[0],
                                           'vendor_code': line[1],
                                           'product_name': line[2],
                                           'price': float(line[3]),
                                           'cantidad': int(float(line[4])),
                                           'delivery_time': int(float(line[5])),
                                           'procesado': False,
                                           'fail': False,
                                           'fail_reason': None
                                          })
                    cont += 1
                if cont == 200:
                    self.env['product.pricelist.load.line'].create(data_line)
                    data_line = []

            if len(data_line) > 0:
                self.env['product.pricelist.load.line'].create(data_line)


    def process_all_products(self):
        for product in self.env['product.template'].search([('active', '=', True)]):
            product.actualizar_precios()

    def process_lines(self):
        if self.replace == True:
            self.env['product.supplierinfo'].search([('name', '=', self.partner_id.id)]).unlink()

        for line in self.file_line_ids.filtered(lambda d: d.procesado == False):
            try:
                if line.code and line.code != '':
                    code = line.code
                    self.update_producto_by_code(line, code, self.partner_id)
                elif line.vendor_code and line.vendor_code != '':
                    vendor_product_code_id = self.env['vendor.product.code'].search([('vendor_code', '=', line.vendor_code), ('partner_id', '=', self.partner_id.id)])
                    code = vendor_product_code_id.product_code
                    self.update_producto_by_code(line, code, self.partner_id)
                self.env.cr.commit()
            except Exception as e:
                self.env.cr.commit()
                line.write({'procesado': False, 'fail': True, 'fail_reason': "{}".format(e)})
        #Genera archivo de excel con las lineas que tienen error
        self.prepare_pricelist_product_values()


    def code_proveedor(self, product_id, supinfo, line):
        if product_id.code_vendor_ids:
            new = True
            if product_id:
                for item in product_id.code_vendor_ids:
                    if supinfo:
                        if item.partner_id.id == supinfo.name.id and item.product_tmpl_id.id == product_id.id and item.vendor_code == line.vendor_code and item.product_code == product_id.default_code:
                            new = False
                            break
            if new:
                if (supinfo and supinfo.name.id) and (product_id and product_id.default_code) and line.vendor_code:
                    product_id.code_vendor_ids.create({'partner_id': supinfo.name.id, 'product_tmpl_id': product_id.id, 'vendor_code': line.vendor_code, 'product_code': product_id.default_code})
        else:
            if (supinfo and supinfo.name.id) and (product_id and product_id.default_code) and line.vendor_code:
                product_id.code_vendor_ids.create({'partner_id': supinfo.name.id, 'product_tmpl_id': product_id.id, 'vendor_code': line.vendor_code, 'product_code': product_id.default_code})


    def update_producto_by_code(self, line, code, partner_id):
        product_id = self.find_product_template(code)
        if product_id:
            supinfo = self.find_supplierinfo_template(product_id, self.company_id, partner_id)
            if supinfo:
                supinfo.write({'price': line.price, 'cantidad': line.cantidad, 'delay': line.delivery_time})
            else:
                supinfo = self.create_supplierinfo(line, product_id, None, partner_id)
            # Se crea la informacion del code proveedor
            self.code_proveedor(product_id, supinfo, line)
            # Actualizamos precio
            if self.partner_id.not_update_prices == False:
                product_id.actualizar_precios()
            line.write({'procesado': True, 'fail': False})
        else:
            product_id = self.find_product(code)
            if product_id:
                supinfo = self.find_supplierinfo_product(product_id, self.company_id, partner_id)
                if supinfo:
                    supinfo.write({'price': line.price, 'cantidad': line.cantidad, 'delay': line.delivery_time})
                else:
                    supinfo = self.create_supplierinfo(line, product_id.product_tmpl_id, product_id, partner_id)
                # Se crea la informacion del code proveedor
                self.code_proveedor(product_id, supinfo, line)
                # Actualizamos precio
                if self.partner_id.not_update_prices == False:
                    product_id.actualizar_precios()
                line.write({'procesado': True, 'fail': False})
            else:
                line.write({'procesado': False, 'fail': True, 'fail_reason': 'PRODUCTO NO ENCONTRADO'})


    def prepare_pricelist_product_values(self):
        file_line_ids = self.file_line_ids.filtered(lambda d: d.fail == True)
        if len(file_line_ids) >= 1:
            self.view_list_error = True
            file_path = 'Export Product with error' + '.xlsx'
            workbook = xlsxwriter.Workbook('/tmp/' + file_path)
            worksheet = workbook.add_worksheet('Product Error')
            header_format = workbook.add_format({'bold': True, 'valign': 'vcenter', 'font_size': 11, 'align': 'center'})
            body_format = workbook.add_format({'valign': 'vcenter', 'font_size': 11, 'align': 'center'})
            worksheet.write((0), 0, 'Product Code', header_format)
            worksheet.write((0), 1, 'Product Name', header_format)
            worksheet.write((0), 2, 'Product Price', header_format)
            worksheet.write((0), 3, 'Quantity', header_format)
            worksheet.write((0), 4, 'Fail Reason', header_format)
            worksheet.write((0), 5, 'Vendor Code', header_format)
            worksheet.write((0), 6, 'Delivery time (days)', header_format)
            rows = 1
            for data in file_line_ids:
                worksheet.write(rows, 0, data.code, body_format)
                worksheet.write(rows, 1, data.product_name, body_format)
                worksheet.write(rows, 2, data.price, body_format)
                worksheet.write(rows, 3, data.cantidad, body_format)
                worksheet.write(rows, 4, data.fail_reason, body_format)
                worksheet.write(rows, 5, data.vendor_code, body_format)
                worksheet.write(rows, 6, data.delivery_time, body_format)
                rows += 1
            workbook.close()
            buf = base64.encodebytes(open('/tmp/' + file_path, 'rb+').read())
            self.file = buf
        else:
            self.view_list_error = False
