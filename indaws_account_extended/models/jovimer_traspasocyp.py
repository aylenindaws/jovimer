# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class JovimerTraspasocyp(models.Model):
    _name = 'jovimer.traspasocyp'
    _description = 'Traspaso Contabilidad Cobros y Pagos'

    name = fields.Char(string='Nombre')
    fecha = fields.Date(string='Fecha Traspaso')
    pagos_ids = fields.Many2many('account.payment', 'rel_account_payment_jovimer_traspasocyp', 'traspaso_id', 'payment_id', string="Pagos Asociados")
    generadiario = fields.Boolean(string='Libro Diario')
    tipotraspaso = fields.Char(string='Tipo Traspaso')

    def creatrasoasocontable(self, context=None):
        hoy = datetime.date.today()
        # traspasoid = self.id
        # namecont = "Traspaso Contable: " + str(hoy) + "."
        self.write({
            'fecha': hoy,
            'name': "Traspaso Contable: " + str(hoy) + ".",
            'tipotraspaso': 'PAGOS',
            'generadiario': True
        })
        # id = str(self.id)
        # args = ["/opt/jovimer12/bin/creatraspasologocontapagos.sh", id, "&"]
        # subprocess.call(args)
        return True