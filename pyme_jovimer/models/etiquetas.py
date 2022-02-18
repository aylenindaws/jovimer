# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import subprocess


class ModelEtiquetas(models.Model):
     
     # Herencia de la tabla de ventas
     _name = 'jovimer_etiquetas'

     name  = fields.Char(string='Nombre de la Etiqueta')
     contenido = fields.Text(string='Contenido Etiqueta TXT BULTO')
     contenidou = fields.Text(string='Contenido Etiqueta TXT UNIDAD')
     contenidohtml = fields.Html(string='Contenido Etiqueta HTML')
     saleorderline = fields.Many2one('sale.order.line', string='Linea de Venta')
     saleorder = fields.Many2one('sale.order', string='Pedido de Venta', related='saleorderline.order_id', store=True)
     purchaseorderline = fields.Many2one('purchase.order.line', string='Linea de Compra')
     purchaseorder = fields.Many2one('purchase.order', string='Pedido de Compra', related='purchaseorderline.order_id', store=True)
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente')
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya')
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name') 
     plantillas = fields.Many2one('jovimer_etiquetas_plantilla', string='Plantilla')	 
     proveedor = fields.Many2one('res.partner', string='Proveedor')



class ModelPlantillaEtiquetas(models.Model):
     
     # Herencia de la tabla de ventas
     _name = 'jovimer_etiquetas_plantilla'

     name  = fields.Char(string='Nombre de la Plantilla de Etiqueta')
     contenido = fields.Text(string='Contenido Etiqueta TXT')
     contenidou = fields.Text(string='Contenido Etiqueta TXT UNIDAD')
     lang = fields.Many2one('res.lang', string='Lenguaje', help='Lengua Nativa de la Etiqueta')
     contenidohtml = fields.Html(string='Contenido Etiqueta Enriquecida')
     plantilla = fields.One2many('jovimer_plantillaproductos', 'plantillaetiquetas', string='Plantilla Producto')
     etiquetas = fields.One2many('jovimer_etiquetas', 'plantillas', string='Plantilla Producto')     
     
