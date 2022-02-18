# -*- coding: utf-8 -*-

from odoo import models, fields, api

class extrapartner(models.Model):
    _inherit = 'res.partner'

    cobrosypagos = fields.One2many('account.invoice', 'partner_id', string='Cobros y Pagos', copy=True, auto_join=True, limit=10)
    docsventas = fields.One2many('sale.order', 'partner_id', string='Documentos Venta', copy=True, auto_join=True, limit=10, domain=[('type_doc', '!=', False)],)
    docscompras = fields.One2many('purchase.order', 'partner_id', string='Documentos Compra', copy=True, auto_join=True, limit=10)
    docsfact = fields.One2many('account.invoice', 'partner_id', string='Facturas', copy=True, auto_join=True, limit=10)
    x_correosrecibidos = fields.One2many('mail.message', 'author_id', string='Correos Recibidos', copy=True, auto_join=True, limit=10)
    x_correosenviados = fields.One2many('mail.mail', 'author_id', string='Correos Enviados', copy=True, auto_join=True, limit=10)
    x_tareas = fields.One2many('project.task', 'partner_id', string='Tareas', copy=True, auto_join=True, limit=10)
    x_eventocalendatio = fields.One2many('calendar.event', 'partner', string='Eventos Calendario', copy=True, auto_join=True, limit=10)
    productosvendidos = fields.One2many('sale.order.line', 'order_partner_id', string='Productos Vendidos', copy=True, auto_join=True, limit=10)
    productoscomprados = fields.One2many('purchase.order.line', 'partner_id', string='Productos Vendidos', copy=True, auto_join=True, limit=10)


    def pyme_action_view_partner_emailr(self):
        self.ensure_one()
        partner = self._ids[0]
        return {
            'name': ("Emails Recibidos"),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.message',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'target': 'current',
            'domain': [('author_id', '=', partner)],
        }


    def pyme_action_view_partner_emaile(self):
        self.ensure_one()
        partner = self._ids[0]
        return {
            'name': ("Emails Enviados"),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.mail',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'target': 'current',
            'domain': [('recipient_ids', '=', partner)],
        }


    def pyme_action_view_partner_tasks(self):
        self.ensure_one()
        partner = self._ids[0]
        return {
        'name': ("Tareas"),
        'type': 'ir.actions.act_window',
        'res_model': 'project.task',
        'view_mode': 'tree,form',
        'view_type': 'form',
        'target': 'current',
        'domain': [('partner_id', '=', partner)],
        }


    def pyme_action_view_partner_calendar(self):
        self.ensure_one()
        partner = self._ids[0]
        return {
        'name': ("Calendario"),
        'type': 'ir.actions.act_window',
        'res_model': 'calendar.event',
        'view_mode': 'tree,form',
        'view_type': 'form',
        'target': 'current',
        'domain': [('partner', '=', partner)],
        }




    def pyme_action_view_partner_sale_vta(self):
        self.ensure_one()
        partner = self._ids[0]
        return {
        'name': ("Documentos Venta"),
        'type': 'ir.actions.act_window',
        'res_model': 'sale.order',
        'view_mode': 'tree,form',
        'view_type': 'form',
        'target': 'current',
        'domain': [('partner_id', '=', partner)],
        }


    def pyme_action_view_partner_invoices_vta(self):
        self.ensure_one()
        partner = self._ids[0]
        return {
        'name': ("Facturas Venta"),
        'type': 'ir.actions.act_window',
        'res_model': 'account.invoice',
        'view_mode': 'tree,form',
        'view_type': 'form',
        'target': 'current',
		'domain': [('partner_id','=',partner)],
        }



    def pyme_action_view_partner_saleline_vta(self):
        self.ensure_one()
        partner = self._ids[0]
        return {
        'name': ("Documentos Venta"),
        'type': 'ir.actions.act_window',
        'res_model': 'sale.order.line',
        'view_mode': 'tree,form',
        'view_type': 'form',
        'target': 'current',
        'domain': [('order_partner_id', '=', partner)],
        }


    def pyme_action_view_partner_purchase_cmp(self):
        self.ensure_one()
        partner = self._ids[0]
        return {
        'name': ("Documentos Compra"),
        'type': 'ir.actions.act_window',
        'res_model': 'purchase.order',
        'view_mode': 'tree,form',
        'view_type': 'form',
        'target': 'current',
        'domain': [('partner_id', '=', partner)],
        }





    def pyme_action_view_partner_invoices_compra(self, context=None):
        self.ensure_one()
        self.env.cr.execute(""" select id from ir_ui_view where name LIKE '%Pyme - Facturas Compra%' and type='tree' ORDER BY id DESC LIMIT 1""")
        result = self.env.cr.fetchone()
        record_id = int(result[0])
        partner = self._ids[0]
        return {
        'name': ("Facturas Compra"),
        'type': 'ir.actions.act_window',
        'res_model': 'account.invoice',
        'view_mode': 'tree',
        'view_type': 'form',
		'view_id': record_id,
        'target': 'current',
		'domain': [('partner_id','=',partner)],
        }



    def pyme_action_view_partner_saleline_compra(self):
        self.ensure_one()
        partner = self._ids[0]
        return {
        'name': ("Productos Comprados"),
        'type': 'ir.actions.act_window',
        'res_model': 'purchase.order.line',
        'view_mode': 'tree,form',
        'view_type': 'form',
        'target': 'current',
        'domain': [('partner_id', '=', partner)],
        }

    def partner_abre_docs(self, context=None):
       cr = self._cr
       uid = self._uid
       ids = self._ids
       parent = self.id

       return {
          'name': ('Pyme - Ventas'),
          'view_type': 'tree,form',
          'view_mode': 'tree,form',
          'res_model': 'sale.order',
          'view_id': False,
          'type': 'ir.actions.act_window',
          'target':'current',
          'partner_id': parent,
       }
	   