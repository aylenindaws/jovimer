# -*- coding: utf-8 -*-

from odoo import models, fields, api

class pedidoVenta(models.Model):
    # Herencia de la tabla de ventas
    _inherit = 'project.task'

    # Añadir el estado Pedido a ventas
    relaciondoc = fields.Many2one('clasificar_tarea', string='Relación')
    rel_idname = fields.Char(related='relaciondoc.name', string="IDREL")
    relacion = fields.One2many('mail.message', 'tareas', string='Relacion Correos', copy=True, auto_join=True)
    eventocalendar = fields.Many2one('calendar.event', string='Calendario', copy=True, auto_join=True)
    etiquetas_tarea = fields.Many2many('etiquetas_relacion', 'etiquetas_tarea', 'tarea_name', string='Tipo de Etiquetas')
    tarea_pr = fields.Many2one('sale.order', string='Presupuestos Venta', domain=[('type_doc','=', 'Presupuesto')], copy=True, auto_join=True)
    tarea_pv = fields.Many2one('sale.order', string='Pedido Venta', domain=[('type_doc','=', 'Pedido')], copy=True, auto_join=True)
    tarea_ab = fields.Many2one('sale.order', string='Albaranes Venta', domain=[('type_doc','=', 'Albaran')], copy=True, auto_join=True)
    tarea_factv = fields.Many2one('account.invoice', string='Facturas', domain=[('type','=', 'out_invoice')], copy=True, auto_join=True)
    tarea_factc = fields.Many2one('account.invoice', string='Facturas', domain=[('type','=', 'in_invoice')], copy=True, auto_join=True)

    def onchange_relacion(self, cr, uid, ids, relacion, context=None):
      if relacion:           
        value = {
	    'country_name': res_country.browse(cr, uid, country_id).name
	    }
      return {'value': value}
