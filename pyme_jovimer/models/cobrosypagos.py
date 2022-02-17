# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import subprocess
from time import sleep
from datetime import datetime, date, time, timedelta
import math
from num2words import num2words




class ModelAccountYPayment(models.Model):
      
     _inherit = 'account.payment'

     # Campos 
     facturas  = fields.Many2many('account.invoice', string='Facturas Relacionada', domain=[('journal_id','in',[11,12,13,14,15,16,17,18,19,20,21,22,23,24])])
     textocarta  = fields.Text(string='Texto Carta')
     fechapagare  = fields.Date(string='Fecha Documento')
     banco  = fields.Many2one('res.bank', string='Cuenta Bancaria')
     diafp  = fields.Char(string='Dia Fecha Pagaré')
     mesfp  = fields.Char(string='Mes Fecha Pagaré')
     anyofp  = fields.Char(string='Año Fecha Pagaré')
     diafd  = fields.Char(string='Dia Fecha Documento')
     mesfd  = fields.Char(string='Mes Fecha Documento')
     anyofd  = fields.Char(string='Año Fecha Documento')
     importetexto = fields.Char(string="Importe")	 
     traspasado = fields.Boolean(string="Traspasado")
     importemillar = fields.Char(string="Importe Millar")
     partnername = fields.Char(string='Partner Name', related='partner_id.name')
     traspasocontfecha = fields.Date(string='Fecha Traspaso')


     def amount_to_text(self, amount):
        self.ensure_one()
        contadec = len(str(amount))
        if contadec == 1:
           amount = str(amount) + "0"
        amount_words = num2words(amount, lang='es')
        return amount_words

     def butonn2w(self):
         valor = self.amount
         valor = str(valor).split('.')
         resultadoa = self.amount_to_text(valor[0])
         resultadod = self.amount_to_text(valor[1])
         resultado = resultadoa + " conf " + resultadod
         resultado = str(resultado).replace('punto cero','') + " Euros"
         self.importetexto = str(resultado)


     def action_imprimetalon(self):
         iddoc = self.id
         fechapago = self.payment_date
         numpagare = self.communication
         importe = self.amount
         importemillar = '{:,.2f}'.format(importe).replace(",", "@").replace(".", ",").replace("@", ".")
         texto = "Adjunto tenemos el gusto de emitir el PAGARÉ Nº " + str(numpagare) + " del BCO. SANTANDER para el próximo dia " + str(fechapago) + " para liquidar las facturas que se detallan a continuación."
         self.write({'textocarta': texto,'importemillar': str(importemillar)})
         return self.env.ref('pyme_jovimer.paymtalonsan_jovimer_report').report_action(self)



     def calcamount(self):	 
         iddoc = self.id
         tipopayment = self.payment_type
         facturas = ""
         total = 0
         importe = 0
         importep = 0
         importec = 0
         ## Cobros
         if tipopayment == "inbound":
          for invoice in self.facturas:
            bloqueada = invoice.bloqueapago
            facturas += str(invoice.id)
            importep = invoice.amount_topay
            importec = invoice.amount_topayc
            importe = invoice.importeapagar
            total = total + importe
         ## Pagos
         if tipopayment == "outbound":
          for invoice in self.facturas:
            facturas += str(invoice.id)
            bloqueada = invoice.bloqueapago
            importep = invoice.amount_topay
            importec = invoice.amount_topayc
            importe =  invoice.importeapagar
            total = total + importe
         ## raise AccessError("EL total es: " + str(total) + "")
         total = round(total, 2)
         valor = total
         valor = str(valor).split('.')
         ## raise AccessError("EL total es: " + str(total) + "")
         if total != 0:
           resultadoa = self.amount_to_text(valor[0])
           resultadod = self.amount_to_text(valor[1])
           resultado = resultadoa + " con " + resultadod
           resultado = str(resultado).replace('punto cero','') + " Euros"
         else:
           resultado = " cero Euros "
         self.amount = float(total)
         self.importetexto = str(resultado)


     @api.onchange('amount')
     def on_change_amount(self):	 
         valor = self.amount
         valor = str(valor).split('.')
         resultadoa = self.amount_to_text(valor[0])
         resultadod = self.amount_to_text(valor[1])
         resultado = resultadoa + " con " + resultadod
         resultado = str(resultado).replace('punto cero','') + " Euros"
         self.importetexto = str(resultado)

     
     @api.onchange('payment_date')
     def on_payment_date(self):
        diafp = ""
        mesfp = ""
        anyofp = ""
        fechapagare = self.payment_date
        if fechapagare != False:
          datetimes_0 = datetime.strptime(str(fechapagare), '%Y-%m-%d')
          if datetimes_0 != False:
             diafp = datetimes_0.strftime("%d")
             mesfp = datetimes_0.strftime("%B")
             anyofp = datetimes_0.strftime("%Y")
          self.diafp = diafp
          self.mesfp = mesfp
          self.anyofp = anyofp


     @api.onchange('fechapagare')
     def on_fechapagare(self):
        diafd = ""
        mesfd = ""
        anyofd = ""
        fechapagare = self.fechapagare
        if fechapagare != False:
          datetimes_0 = datetime.strptime(str(fechapagare), '%Y-%m-%d')
          if datetimes_0 != False:
             diafd = datetimes_0.strftime("%d")
             mesfd = datetimes_0.strftime("%B")
             anyofd = datetimes_0.strftime("%Y")
          self.diafd = diafd
          self.mesfd = mesfd
          self.anyofd = anyofd


     @api.onchange('journal_id')
     def on_journal_id(self):
         iddoc = self._origin.id
         idjournal = self.journal_id
         journalbank = self.journal_id.banco		 
         if journalbank != False:
            self.banco = journalbank


     @api.onchange('facturas')
     def on_amount(self):
         iddoc = self._origin.id
         tipopayment = self.payment_type
         facturas = ""
         total = 0
         importe = 0
         importep = 0
         importec = 0
         ## Cobros
         if tipopayment == "inbound":
          for invoice in self.facturas:
            bloqueada = invoice.bloqueapago
            facturas += str(invoice.id)
            importep = invoice.amount_topay
            importec = invoice.amount_topayc
            importe = importec - importep
            if bloqueada != True:
               invoice.importeapagar = importe
               invoice.pagadopy = True
               invoice.pagadopy = True
               invoice.bloqueapago = True
            total = total + importe
         ## Pagos
         if tipopayment == "outbound":
          for invoice in self.facturas:
            facturas += str(invoice.id)
            bloqueada = invoice.bloqueapago
            importep = invoice.amount_topay
            importec = invoice.amount_topayc
            importe =  importep -importec
            if bloqueada != True:
               invoice.importeapagar = importe
               invoice.pagadopy = True
               invoice.bloqueapago = True
            total = total + importe
         ## raise AccessError("EL total es: " + str(total) + "")
         total = round(total, 2)
         valor = total
         valor = str(valor).split('.')
         if total != 0:
           resultadoa = self.amount_to_text(valor[0])
           resultadod = self.amount_to_text(valor[1])
           resultado = resultadoa + " con " + resultadod
           resultado = str(resultado).replace('punto cero','') + " Euros"
         else:
           resultado = " cero Euros "
         self.amount = float(total)
         self.importetexto = str(resultado)


     def cancel2(self):
        for rec in self:
            for invoice in rec.facturas:
             bloqueada = invoice.bloqueapago
             if bloqueada == True:
               invoice.bloqueapago = False
            for move in rec.move_line_ids.mapped('move_id'):
                if rec.invoice_ids:
                    move.line_ids.remove_move_reconcile()
                if move.state != 'draft':
                    move.button_cancel()
                move.unlink()
            rec.write({
                'state': 'cancelled',
            })



     def post2(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconcilable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to draft

            ## Sincronizamos
            resultadoa = rec.calcamount()
            for invoice in rec.facturas:
             bloqueada = invoice.bloqueapago
             if bloqueada != True:
               invoice.bloqueapago = True


            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)
            persist_move_name = move.name

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()
                persist_move_name += self._get_move_name_transfer_separator() + transfer_debit_aml.move_id.name

            rec.write({'state': 'posted', 'move_name': persist_move_name})
        return True




class ModelAccountInvoice(models.Model):
      
     _inherit = 'account.invoice'

     def _creafechapago(self):
        for rec in self:
            fecha = False
            if rec.tipodiariopago == "sale":
               fecha = rec.date_invoice
            if rec.tipodiariopago == "purchase":
               fecha = rec.dateinv_compra
            if fecha != False:
               rec.fechafacturapago = fecha
            ## totalkg = 0
            ## for line in rec.invoice_line_ids:
            ##     if line.product_id:
            ##         totalkg += line.totalkglin or 0.0
            ## rec.totalkg = totalkg


     def _compute_cobro(self):
        for rec in self:
            cobro = False
            if rec.journal_id.type == "sale":
                cobro = True
            rec.cobro = cobro

     def _compute_pago2(self):
        for rec in self:
            pago2 = False
            if rec.journal_id.type == "purchase":
               pago2 = True
            rec.pago2 = pago2


     # Campos 
     tipodiariopago  = fields.Selection([('sale', 'Sale'),('purchase', 'Purchase'),('cash', 'Cash'),('bank', 'Bank'),('general', 'Miscellaneous'),], related='journal_id.type')
     pagadopy = fields.Boolean(string='Pagado')
     fechafacturapago = fields.Date(string='Fecha Fatura Buscador')
     importeapagar = fields.Float(string='Importe Pagado')
     amount_topay = fields.Float(string='Proveedor')
     amount_topayc = fields.Float(string='Cliente')
     bloqueapago = fields.Boolean(string='Bloquea Pagado')
     cobro = fields.Boolean(string='cobro', compute='_compute_cobro')
     pago2 = fields.Boolean(string='pago', compute='_compute_pago2')
     listapago = fields.One2many('account.payment','facturas',string='Pagos')



     def quitarpago(self):
         iddoc = self.id
         self.write({'bloqueapago': False, 'pagadopy': False})
         raise AccessError("NO se puede Eliminar El PAGO")

     def parcial(self):
         iddoc = self.id
         importeapagar = self.importeapagar
         self.write({'importeapagar': importeapagar})



class ModelAccountJournal(models.Model):
      
     _inherit = 'account.journal'


     cuentabanco = fields.Boolean(string='Pagado')
     banco  = fields.Many2one('res.bank', string='Cuenta Bancaria')
	 
	 
	 
	 
	 
	 
	 