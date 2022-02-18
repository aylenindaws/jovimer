# -*- coding: utf-8 -*-

from odoo import models, fields, api

class pymeproducttmpl(models.Model):
	_inherit = 'product.template'
	
	@api.multi
	def _get_total(self, name=None):
		
		self._cr.execute("""select sum(product_uom_qty) from sale_order_line where product_id='8' AND order_id in (select id from sale_order where type_doc='Pedido');""")
		for resv in self.env.cr.fetchone():
			almpteenv = str(resv)
			self._cr.execute("""update product_template set almpteenv = '""" + almpteenv + """';""")
			return almpteenv

		self._cr.execute("""select sum(product_qty) from purchase_order_line where product_id='8' AND order_id in (select id from purchase_order where state='pedido');""")
		for resc in self.env.cr.fetchone():
			almpterec = str(resc)
			self._cr.execute("""update product_template set almpterec = '""" + almpterec + """';""")
			return almpterec

			
			

	almexist = fields.Char('Stock Actual', help="Existencias en Almacén")
	almstini = fields.Char('Existencias Inciales', help="Inventario Incicial")
	almpterec = fields.Char('Pendiente de Recibir', help="Cantidad Pendiente de Recibir. Pedidos sin Albarán de Entrada")
	almpteenv = fields.Char('Pendiente de Servir', help="Cantidad Pendiente de Servir. Pedidos sin Albarán de Salida")
	almexiste = fields.Char('Stock Previsto', compute='_get_total', help="Stock Actual + Pendiente de Recibir - Pendiente de Servir")
	x_disponi = fields.One2many('stock.quant', 'product_tmpl_id', string='Eventos Calendario', copy=True, auto_join=True)
	precioultcompra = fields.Char('Precio Ultima Compra')
	preciomedio = fields.Char('Precio Medio')
    
