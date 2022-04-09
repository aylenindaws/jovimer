# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'

    traspasocont = fields.Boolean('Traspasado Contabilidad')

    def get_invoices_clients(self):
        self.env.cr.execute("""
                    select id from account_move am 
                    where am.traspasocont is null 
                    and am.state not in ('draft', 'cancel') 
                    and move_type in ('out_invoice','out_refund') 
                    and id not in (select move_id from rel_account_move_jovimer_traspasoconta);
        """)
        res = self.env.cr.fetchall()
        if len(res):
            ids = []
            for id in res:
                ids.append(id[0])
            self.env["jovimer.traspasoconta"].create({
                'name': "Traspaso Contable Clientes: " + str(datetime.date.today()) + ".",
                'tipotraspaso': 'EMITIDAS',
                'invoices_ids': [(6, 0, ids)]
            })

    def get_invoices_supplier(self):
        self.env.cr.execute("""
                    select id from account_move am 
                    where am.traspasocont is null 
                    and am.state not in ('draft', 'cancel') 
                    and move_type in ('in_invoice','in_refund') 
                    and id not in (select move_id from rel_account_move_jovimer_traspasoconta);
        """)
        res = self.env.cr.fetchall()
        if len(res):
            ids = []
            for id in res:
                ids.append(id[0])
            self.env["jovimer.traspasoconta"].create({
                'name': "Traspaso Contable Proveedores: " + str(datetime.date.today()) + ".",
                'tipotraspaso': 'RECIBIDAS',
                'invoices_ids': [(6, 0, ids)]
            })

