# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    traspasado = fields.Boolean(string="Traspasado")

    def get_payments(self):
        self.env.cr.execute("""
                    select id from account_payment ap 
                    where ap.traspasado is null 
                    and id not in (select payment_id from rel_account_payment_jovimer_traspasocyp);
        """)
        res = self.env.cr.fetchall()
        if len(res):
            ids = []
            for id in res:
                ids.append(id[0])
            self.env["jovimer.traspasocyp"].create({
                'name': "Traspaso Contable Pagos: " + str(datetime.date.today()) + ".",
                'tipotraspaso': 'PAGOS',
                'pagos_ids': [(6, 0, ids)]
            })