# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

class pedidoVenta(models.Model):
    # Herencia de la tabla de ventas
    _inherit = 'sale.order'


    def _method_name3(self):
        return [
        ('draft', 'Activo'),
        ('sent', 'Enviado'),
        ('sale', 'Para Facturar'),
        ('done', 'Pendiente Facturar'),
        ('apedido', 'Pasado a Pedido'),
		('aalbaran', 'Pasado a Albarán'),
		('afactura', 'Pasado a Factura'),
		('cancel', 'Cancelar'),
        ]



    # Añadir el estado Pedido a ventas
    state = fields.Selection(selection_add=[('apedido', 'Pasado a Pedido'),('aalbaran', 'Pasado a Albarán')])
    relacionmailpr = fields.One2many('mail.message', 'venta_pr', string="Relación")
    relacionmailpv = fields.One2many('mail.message', 'venta_pv', string="Relación")
    relacionmailab = fields.One2many('mail.message', 'venta_ab', string="Relación")
    relaciontareapr = fields.One2many('project.task', 'tarea_pr', string="Relación Tarea")
    relaciontareapv = fields.One2many('project.task', 'tarea_pv', string="Relación Tarea")
    relaciontareaab = fields.One2many('project.task', 'tarea_ab', string="Relación Tarea")
    docwix = fields.Many2one('sale.order', string="Relacion Documentos Venta")
    docrel2 = fields.One2many('sale.order.rel', 'docrel', string="Relacion Documentos Venta")
    subject = fields.Integer(string='Subject', help="Subject of document.")
    numero = fields.Char(store=True, readonly=False)
    type_doc = fields.Selection([
		('Presupuesto','Presupuesto'),
		('Pedido','Pedido'),
		('Albaran','Albarán'),
		],string='TipoDoc',default='Pedido')
    type_sale = fields.Selection([
		('abierta','Abierto'),
		('apedido', 'Pasado a Pedido'),
		('aalbaran', 'Pasado a Albarán'),
		('afactura', 'Pasado a Factura'),
        ('cancelado', 'Cancelado'),
		],string='Estado')
    type_idname = fields.Char(string='Type ID NAME', related='type_id.name')
    nextnum = fields.Char(string='Nextnum', store=True)
    state = fields.Selection(_method_name3, string='Estado', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    @api.model
    def create(self, vals):

        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.order') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _('New')

        ##### Personalizacion ########

        numeros = self.env['sale.order'].browse(vals.get('numero'))
        numpedid = str(vals['numero'])
        numped = numpedid
        idnumped = int(numped)
        serieid = int(vals['type_id'])

        self.env.cr.execute(""" select type_doc from sale_order_type where  id=%s""" % (serieid))
        result = self.env.cr.fetchone()
        type_doc = result[0]

        
        self.env.cr.execute(""" select name from sale_order_type where  id=%s""" % (serieid))
        result = self.env.cr.fetchone()
        seriep = result[0]

        if seriep=='SELECCIONA >':
                    raise UserError(_('Debes Seleccionar una Serie y Numero Valido para el Docuento Actual'))
        self.env.cr.execute(""" UPDATE sale_order_type SET nextnum=%s + 1 where id=%s""" % (idnumped,serieid))
        vals['name'] = seriep + '/' + numped + ''
        ## vals['type_doc'] = type_doc
        vals['type_sale'] = 'apedido'
        ##############################


        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
        result = super(pedidoVenta, self).create(vals)
        return result

    

    @api.onchange('type_id')
    def _compute_numero(self):
             self.env.cr.execute("""select nextnum from sale_order_type where id='%d' ORDER BY id DESC LIMIT 1""" % (self.type_id)) # few inner joins and where conditions
             result = self.env.cr.fetchone()
             nextnum = result[0]
             if nextnum == "":
                 nextnum = 0
             self.numero = nextnum
             return {}

    # Metodo que llamará un botón para cambiar el estado a pedido

    def action_pedido(self, default=None):
        for order in self:
           tx = order.sudo().transaction_ids.get_last_transaction()
           if tx and tx.state == 'pending' and tx.acquirer_id.provider == 'transfer':
                tx._set_transaction_done()
                tx.write({'is_processed': True})
        
           self.write({'state': 'sale'})
           self.write({'type_sale': 'apedido'})
           ## Buscamos la default
           self.env.cr.execute("""select id from sale_order_type where type_doc='Pedido' ORDER BY id DESC LIMIT 1""")
           resultp = self.env.cr.fetchone()
           tipoped = resultp[0]
           default = dict(default or {})
           default.update({
		   'note': '',
		   'type_id': tipoped,
		   'type_doc': 'Pedido',
		   'origin': self._ids[0],
		   'docwix': self._ids[0],
		   ## 'numero': _compute_numero,
		   'state': 'draft',
           'type_sale': 'abierta'})
           super(pedidoVenta, self).copy(default)
           self.env.cr.execute(""" select id from sale_order WHERE type_doc='Pedido' ORDER BY id DESC LIMIT 1""")
           result = self.env.cr.fetchone()
           record_id = int(result[0])
           self.env.cr.execute(""" INSERT INTO sale_order_rel ("docrel","desc","docrel2","desc2","docrel3","desc3") VALUES ('%s','FUENTE','%s','DESTINO','%s','ORIGEN')""" % (self._ids[0],record_id,self._ids[0]))
           self.env.cr.execute(""" INSERT INTO sale_order_rel ("docrel","desc","docrel2","desc2","docrel3","desc3") VALUES ('%s','FUENTE','%s','DESTINO','%s','ORIGEN')""" % (record_id,record_id,self._ids[0]))
        
        return {
                'name': ("Pedidos Venta"),				
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
                'context': "{}",
                'docwix': record_id,
                'res_id': record_id  or False,
            }



    def action_albaran(self, default=None):
        for order in self:
           tx = order.sudo().transaction_ids.get_last_transaction()
           if tx and tx.state == 'pending' and tx.acquirer_id.provider == 'transfer':
                tx._set_transaction_done()
                tx.write({'is_processed': True})

           self.write({'state': 'sale'})
           self.write({'type_sale': 'aalbaran'})
            ## Buscamos la default
           self.env.cr.execute("""select id from sale_order_type where type_doc='Albaran' ORDER BY id DESC LIMIT 1""")
           resultp = self.env.cr.fetchone()
           tipoped = resultp[0]
           default = dict(default or {})
           default.update({
		   'note': '',
		   'type_id': tipoped,
		   'type_doc': 'Albaran',
		   'state': 'draft',
           'type_sale': 'abierta'})
           super(pedidoVenta, self).copy(default)
           self.env.cr.execute(""" select id from sale_order WHERE type_doc='Albaran' ORDER BY id DESC LIMIT 1""")
           result = self.env.cr.fetchone()
           record_id = int(result[0])
           self.env.cr.execute(""" INSERT INTO sale_order_rel ("docrel","desc","docrel2","desc2","docrel3","desc3") VALUES ('%s','FUENTE','%s','DESTINO','%s','ORIGEN')""" % (self._ids[0],record_id,self._ids[0]))
           self.env.cr.execute(""" INSERT INTO sale_order_rel ("docrel","desc","docrel2","desc2","docrel3","desc3") VALUES ('%s','FUENTE','%s','DESTINO','%s','ORIGEN')""" % (record_id,record_id,self._ids[0]))
           return {
                'name': ("Pedidos Venta"),				
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
                'context': "{}",
                'docwix': record_id,
                'res_id': record_id  or False,
           }


    def action_view_invoice2(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form2').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action







    def copy_sale(self, default=None):
        default = dict(default or {})
        super(pedidoVenta, self).copy(default)
        return {
                'name': ("Pedidos Venta"),				
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
                'context': "{}",
                'docwix': record_id,
                'res_id': record_id  or False,
            }
    def action_borrar(self, default=None):
        default = dict(default or {})
        for order in self:
             ## if order.state not in ('draft', 'cancel'):
             ##      raise UserError(_('No se puede Eliminar un Documento que referencia a uno superior'))
             self.write({'state': 'cancel'})
             self.env.cr.execute(""" DELETE FROM sale_order_rel where "docrel"='%s' """ % (self._ids[0]))
             super(pedidoVenta, order).unlink()
             ## res = super(pedidoVenta, order).unlink()
             return { }

    def action_crea_factura(self, grouped=False, final=False):
        self.write({'state': 'sale'})
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)
            for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice < 0):
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                elif group_key in invoices:
                    vals = {}
                    if order.name not in invoices[group_key].origin.split(', '):
                        vals['origin'] = invoices[group_key].origin + ', ' + order.name
                    if order.client_order_ref and order.client_order_ref not in invoices[group_key].name.split(', ') and order.client_order_ref != invoices[group_key].name:
                        vals['name'] = invoices[group_key].name + ', ' + order.client_order_ref
                    invoices[group_key].write(vals)
                if line.qty_to_invoice > 0:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
                elif line.qty_to_invoice < 0 and final:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoice] = references[invoice] | order

        if not invoices:
            raise UserError(_('There is no invoicable line.'))

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoicable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]
	
    def sale_abre_form(self, context=None):
       cr = self._cr
       uid = self._uid
       ids = self._ids
       parent = self.id

       return {
          'name': ('Pyme - Lineas de Venta'),
          'view_type': 'form',
          'view_mode': 'form',
          'res_model': 'sale.order.line',
          'view_id': False,
          'type': 'ir.actions.act_window',
          'target':'new'
       }

    
	
    def calculanumerovta(self, default=None):
        self.name='HOLA'
        return super(pedidoVenta, self)




class pedidoVentaLineas(models.Model):
    # Herencia de la tabla de ventas
    _inherit = 'sale.order.line'



	
    def sale_abre_form(self, context=None):
       cr = self._cr
       uid = self._uid
       ids = self._ids
       parent = self.id

       return {
          'name': ('Pyme - Lineas de Venta'),
          'view_type': 'form',
          'view_mode': 'form',
          'res_model': 'sale.order.line',
          'view_id': False,
		  'res_id': parent,
          'type': 'ir.actions.act_window',
          'target':'new'
       }

class tipopedidoVenta(models.Model):
    # Herencia de la tabla de ventas
    _inherit = 'sale.order.type'

    # Añadir el estado Pedido a ventas
    ## proximonumerov = fields.Integer(string='Next Number', help='Proximo numero según secuencia.', compute='_compute_seq_number_vnext')
    proximonumerov = fields.Integer(string='Next Number', help='Proximo numero según secuencia.', related='sequence_id.number_next_actual')
    discount_fixed = fields.Float(string="Discount (Importe)")


    def _compute_seq_number_vnext(self):
        '''Añadimos un campo por la secuencia calculada
        '''
        if self.sequence_id:
           proximonumerov = self.sequence_id.number_next_actual
        else:
           proximonumerov = 1

class TrazabilidadVenta(models.Model):
    _name = "sale.order.rel"
    _description = "Relacion Documentos Venta"
    _order = 'id desc'

    docrel = fields.Many2one('sale.order', string="Relacion Documentos Venta")
    desc = fields.Char(string='Tipo Relacion')
    docrel2 = fields.Many2one('sale.order', string="Relacion Documentos Venta")
    desc2 = fields.Char(string='Tipo Relacion')
    docrel3 = fields.Many2one('sale.order', string="Relacion Documentos Venta")
    desc3 = fields.Char(string='Tipo Relacion')



class pedidoCompra(models.Model):
    # Herencia de la tabla de ventas
    _inherit = 'purchase.order'

    # Añadir el estado Pedido a ventas
    state = fields.Selection(selection_add=[('pedido', 'Pedido')])

    # Metodo que llamará un botón para cambiar el estado a pedido

    def action_pedido(self):
        return self.write({'state': 'pedido'})