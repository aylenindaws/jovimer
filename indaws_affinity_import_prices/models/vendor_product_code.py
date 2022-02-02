from odoo import models, fields, api, _, exceptions



class vendor_product_code(models.Model):
    _name = 'vendor.product.code'

    partner_id = fields.Many2one('res.partner', string="Vendor", required=True)
    product_tmpl_id = fields.Many2one('product.template', string="Product")
    vendor_code = fields.Char(string="Vendor Code")
    product_code = fields.Char(string="Product Code", related='product_tmpl_id.default_code', store=True)

    _sql_constraints = [
        ('indaws_partner_id_vendor_code_uniq', 'unique(partner_id,vendor_code)',
         "No se puede guardar el Vendor Code del producto. ! \n\nPor favor valide que la informacion relacionada con el vendor code para que no este asociada a otro producto.")
    ]