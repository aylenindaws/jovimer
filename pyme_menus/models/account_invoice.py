# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

class FacturasCompraVenta(models.Model):
    # Herencia de la tabla de ventas
    _inherit = 'account.invoice'

    ### _defaults={
    ###    'date_invoice': date.today().strftime('%Y-%m-%d'),
    ### }

    def _method_name2(self):
        return [('draft', 'Activa'), ('open', 'Contabilizada'),('paid', 'Pagada'),('cancel', 'Cancelada')]

 	# Añadir el estado Pedido a ventas
    dateinv_compra = fields.Date(string='Fecha Factura Compra', readonly=True, states={'draft': [('readonly', False)]}, index=True, help="Vacio para Fecha Actual", copy=False)
    relaciontareafv = fields.One2many('project.task', 'tarea_factv', string="Relación Tarea")
    relaciontareafc = fields.One2many('project.task', 'tarea_factc', string="Relación Tarea")
    relacionmail = fields.One2many('mail.message', 'factura', string="Relación Mail")
    numbernext = fields.Integer(related='journal_id.sequence_id.number_next', store=False, readonly=False, copy=False)
    
    state = fields.Selection(_method_name2, string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)

    @api.onchange('dateinv_compra')
    def on_change_dateinv_compra(self):
        fechainv = self.dateinv_compra
        self.date_invoice = fechainv
        return {}

    def action_invoice_cancel_pymetree(self):
         ### if self.filtered(lambda inv: inv.state not in ['draft', 'open']):
         ###     raise UserError(_("Las Facturas Pagadas No pueden cancelarse si no se eliminan los Pagos o Cobros Primero."))
         if self.bloqueapago == True:
            raise AccessError("Las Facturas con PAGOS realizados NO pueden ser modificadas y/o canceladas")
         return self.action_cancel()

    def action_invoice_cancel_pyme(self):
         ### if self.filtered(lambda inv: inv.state not in ['draft', 'open']):
         ###     raise UserError(_("Las Facturas Pagadas No pueden cancelarse si no se eliminan los Pagos o Cobros Primero."))
         if self.bloqueapago == True:
            raise AccessError("Las Facturas con PAGOS realizados NO pueden ser modificadas y/o canceladas")
         return self.action_cancel()


    def action_invoice_cancel_pyme2(self):
         ### if self.filtered(lambda inv: inv.state not in ['draft', 'open']):
         ###     raise UserError(_("Las Facturas Pagadas No pueden cancelarse si no se eliminan los Pagos o Cobros Primero."))
         if self.bloqueapago == True:
            raise AccessError("Las Facturas con PAGOS realizados NO pueden ser modificadas y/o canceladas")
         context = self._context
         current_uid = context.get('uid')
         if current_uid == 17 or current_uid == 20:
             self.write({'traspasocont': False})
             self.write({'traspasocontfecha': False})
             return self.action_cancel()
         else:            
             raise AccessError("No tienes Permiso para poder Cancelar una Factura COntabilizada. El Usario con permiso: Miguel Sanfelix y Anais Reig - administracion")



    def action_invoice_open_pyme(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
            raise UserError(_("Para contabilizar la Factura debe estar en estado Activa."))
        if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
            raise UserError(_("No se puede contabilidar una Factura con Importes Negativos. Realice un Abono."))
        if to_open_invoices.filtered(lambda inv: inv.amount_total == 0):
            raise UserError(_("No se puede contabilidar una Factura con importe igual a 0."))

        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()

    @api.model
    def create2(self, vals):
        if not vals.get('journal_id') and vals.get('type'):
            vals['journal_id'] = self.with_context(type=vals.get('type'))._default_journal().id

        onchanges = self._get_onchange_create()
        for onchange_method, changed_fields in onchanges.items():
            if any(f not in vals for f in changed_fields):
                invoice = self.new(vals)
                getattr(invoice, onchange_method)()
                for field in changed_fields:
                    if field not in vals and invoice[field]:
                        vals[field] = invoice._fields[field].convert_to_write(invoice[field], invoice)
        bank_account = self._get_default_bank_id(vals.get('type'), vals.get('company_id'))
        if bank_account and not vals.get('partner_bank_id'):
            vals['partner_bank_id'] = bank_account.id

        ## raise UserError(_('Has cambiado el JOurnal'))
        ## serieid = str(self[0].journal_id[0].id)
        ## seriename  = str(self[0].journal_id[0].name)
        

        journal=str(vals.get('journal_id'))
        self.env.cr.execute(""" select code from account_journal where id=%s """ % (journal))
        result = self.env.cr.fetchone()
        seriename = str(result[0])
        serieid = str(vals.get('numbernext'))
        ## raise UserError(_('Tienes esto: ' + seriename + '/' + serieid))
        vals['move_name']  = seriename + '/' + serieid
        nexnum=vals.get('numbernext') + 1
        self.env.cr.execute(""" UPDATE ir_sequence SET number_next=%s + 1  where id in (select sequence_id from account_journal where id=%s) """ % (nexnum,journal))
        invoice = super(FacturasCompraVenta, self.with_context(mail_create_nolog=True)).create(vals)

        if any(line.invoice_line_tax_ids for line in invoice.invoice_line_ids) and not invoice.tax_line_ids:
            invoice.compute_taxes()

        for inv in self:
            # Here the onchange will automatically write to the database
            inv._onchange_payment_term_date_invoice()
        
        return invoice


    def action_invoice_cancelpyme(self):
       self.filtered(lambda inv: inv.state != 'cancel').action_cancel()
       # We also clean reference for compatibility with argentinian loc
       for rec in self:
           # if document type has a sequence then a new sequence must be
           # requested. Otherwise, we want to keep number introduced by user
           if 'document_sequence_id' in rec._fields and \
                   rec.document_sequence_id:
               rec.write({
                   'move_name': False,
                   'document_number': False})
           else:
               rec.write({'move_name': False})

       for invoice in self:
            if invoice.state not in ('draft', 'cancel'):
                raise UserError(_('No se puede Eliminar la Factura en este caso. Comprueba que no este referida a un Pago y/o registro en el un Libro de Facturas Confirmado'))
            elif invoice.move_name:
                raise UserError(_('No se puede Eliminar la Factura en este caso. Comprueba que no este referida a un Pago y/o registro en el un Libro de Facturas Confirmado'))
            invoice.unlink()
            return {
                'name': 'Facturas',
                'type': 'ir.actions.act_window',
                'res_model': 'account.invoice',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'target': 'current',
                ## 'domain': [('id', 'in', invoice)]
            }
 

 


class DiariosContables(models.Model):
    # Herencia de la tabla de ventas
    _inherit = 'account.journal'
    
    # Añadir el estado Pedido a ventas
    habitual = fields.Boolean(string='Habitual')
    description = fields.Text(string='Descripcion', translate=True)
    numbernext = fields.Integer(related='sequence_id.number_next', store=False, readonly=False, copy=False)