# -*- coding: utf-8 -*-

from odoo import models, fields, api

class pedidoCompra(models.Model):
    # Herencia de la tabla de ventas
    _inherit = 'purchase.order'

    # Añadir el estado Pedido a ventas
    state = fields.Selection(selection_add=[('apedido', 'Pasado a Pedido'),('aalbaran', 'Pasado a Albarán')])
    relacionmail = fields.One2many('mail.message', 'pedido_venta', string="Relación")
    relacionmailpr = fields.One2many('mail.message', 'compra_pr', string="Relación")
    relacionmailpv = fields.One2many('mail.message', 'compra_pv', string="Relación")
    relacionmailab = fields.One2many('mail.message', 'compra_ab', string="Relación")
    subject = fields.Char(string='Subject', help="Subject of document.")
    type_doc = fields.Selection([
		('Presupuesto','Presupuesto'),
		('Pedido','Pedido'),
		('Albaran','Albarán'),
		],string='TipoDoc')

    # Metodo que llamará un botón para cambiar el estado a pedido

    def action_pedidocu(self, default=None, context=None):
        self.write({'state': 'apedido'})
        default = dict(default or {})
        default.update({
        'note': '',
        ## 'type_id': 6,
        'type_doc': 'Pedido',
		'state': 'draft'})
        newpo = super(pedidoCompra, self).copy(default)
        return newpo


    def action_pedidoc(self, default=None):
        new_po = super(pedidoCompra, self).copy(default=default)
        for line in new_po.order_line:
            seller = line.product_id._select_seller(
                partner_id=line.partner_id, quantity=line.product_qty,
                date=line.order_id.date_order and line.order_id.date_order[:10], uom_id=line.product_uom)
            line.date_planned = line._get_date_planned(seller)
        return new_po

    def action_albaranc(self, default=None):
        self.write({'state': 'aalbaran'})
        default = dict(default or {})
        default.update({
		'note': '',
		## 'type_id': 7,
		'type_doc': 'Albaran',
		'state': 'draft'})
        return super(pedidoCompra, self).copy(default)

    def action_facturarc(self, default=None):
        self.write({'state': 'purchase'})
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = {'type': 'in_invoice', 'default_purchase_id': self.id}

        if not self.invoice_ids:
            # Choose a default account journal in the same currency in case a new invoice is created
            journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id),
                ('currency_id', '=', self.currency_id.id),
            ]
            default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
            if default_journal_id:
                result['context']['default_journal_id'] = default_journal_id.id
        else:
            # Use the same account journal than a previous invoice
            result['context']['default_journal_id'] = self.invoice_ids[0].journal_id.id

        #choose the view_mode accordingly
        if len(self.invoice_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        elif len(self.invoice_ids) == 1:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.invoice_ids.id
        return result

    def copy_purchase(self, default=None):
        default = dict(default or {})
        return super(pedidoCompra, self).copy(default)

class pedidoCompraLineas(models.Model):
    # Herencia de la tabla de ventas
    _inherit = 'purchase.order.line'



	
    def purchase_abre_form(self, context=None):
       cr = self._cr
       uid = self._uid
       ids = self._ids
       parent = self.id
        
       return {
          'name': ('Pyme - Lineas de Compra'),
          'view_type': 'form',
          'view_mode': 'form',
          'res_model': 'purchase.order.line',
          'view_id': False,
		  'res_id': parent,
          'type': 'ir.actions.act_window',
          'target':'new'
       }

	
    def purchase_abre_asig(self, context=None):
       cr = self._cr
       uid = self._uid
       ids = self._ids
       parent = self.id
        
       return {
          'name': ('Asignaciones'),
          'view_type': 'form',
          'view_mode': 'form',
          'res_model': 'jovimer_asignaciones',
          'view_id': False,
		  ## 'res_id': parent,
          'type': 'ir.actions.act_window',
          'target':'new'
       }



       
    
