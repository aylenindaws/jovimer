# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
import base64

class JovimerTraspasoconta(models.Model):
    _name = 'jovimer.traspasoconta'
    _description = 'Traspaso Contabilidad'

    name = fields.Char(string='Nombre')
    fecha = fields.Date(string='Fecha Traspaso')
    invoices_ids = fields.Many2many('account.move', 'rel_account_move_jovimer_traspasoconta', 'traspaso_id', 'move_id', string="Facturas Afectadas")
    generaiva = fields.Boolean(string='Libro de Iva')
    generadiario = fields.Boolean(string='Libro Diario')
    tipotraspaso = fields.Char(string='Tipo Traspaso')
    archivo = fields.Binary('Reporte TXT')

    # facturas emitidas
    def report_invoices_clients_txt(self):
        hoy = datetime.date.today()
        data = ''
        for item in self.invoices_ids:
            FECHAFACT = str(item.invoice_date.day).rjust(2, '0') + str(item.invoice_date.month).rjust(2, '0')
            FECHAOP = "00000000"
            NUMFACT = item.name + ''.ljust(12)
            NUMFACR = "                  "
            NOMBLIPROV = self.get_name_partner(item.partner_id)
            NIF = item.partner_id.vat.ljust(20)[0:20] if item.partner_id.vat else ''.ljust(20)
            NUMSR = "E"
            BASE = str(item.amount_untaxed * -1 if (item.move_type == "out_refund" or item.move_type == "in_refund") else item.amount_untaxed)
            ANYO = str(item.invoice_date.year)
            MES = str(item.invoice_date.month).rjust(2, '0')
            RYF = "F1    01" if (item.move_type == "out_refund" or item.move_type == "in_refund") else "F1    01"
            E5SUJTAI = "E E5"
            CONCEPTO = "VENTA MERCADERIAS"
            # data += FECHAFACT + " " + FECHAOP + " " + NUMFACT + " " + NUMFACR + " " + NOMBLIPROV + " " + NIF + " " + NUMSR + " " + BASE + "     0                 0,00                                                 " + ANYO + " " + MES + " " + RYF + " " + E5SUJTAI + " " + CONCEPTO + "\n"

            data += FECHAFACT + " " + FECHAOP + " " + NUMFACT + " " + NUMFACR + " " + NOMBLIPROV + " " + NIF + " "+NUMSR +"     "+BASE+"     0                 0,00                                                 "+ANYO + " " + MES +'                      '+RYF+'                                             '+ E5SUJTAI+"                                       0,00                                                                                                                                                                                              0,00                                                                                               "+CONCEPTO+"                                                                                                                                                                                                                                                                                                                                                          "

            item.traspasocont = True
        self.write({
            'archivo': base64.encodestring(bytes(data, "utf-8")),
            'fecha': hoy,
            'name': "Traspaso Contable: " + str(hoy) + ".",
            'tipotraspaso': 'EMITIDAS',
            'generaiva': True,
            'generadiario': True
        })
        return {
            'name': 'Report',
            'type': 'ir.actions.act_url',
            'url': (
                    "web/content/?model=" +
                    self._name + "&id=" + str(self.id) +
                    "&filename_field=name&field=archivo&download=true&filename=" +
                    self.name + '.txt'
            ),
            'target': '_new',
        }

    def get_name_partner(self, partner):
        if partner and partner.nomfiscal:
            return partner.nomfiscal.ljust(50)[0:50]
        elif partner and partner.name:
            return partner.name.ljust(50)[0:50]
        else:
            return ''.ljust(50)

    #crear txt facturas proveedor
    def creatrasoasocontablec(self):
        hoy = datetime.date.today()
        data = ''
        for item in self.invoices_ids:
            FECHAFACT = str(item.invoice_date.day).rjust(2, '0') + str(item.invoice_date.month).rjust(2, '0')
            FECHAOP = "00000000"
            NUMFACT = item.name + ''.ljust(12)
            NUMFACR = "                  "
            NOMBLIPROV = self.get_name_partner(item.partner_id)
            NIF = item.partner_id.vat.ljust(20)[0:19] if item.partner_id.vat else ''.ljust(20)
            NUMSR = "E"
            BASE = str(item.amount_untaxed * -1 if (item.move_type == "out_refund" or item.move_type == "in_refund") else item.amount_untaxed)
            ANYO = str(item.invoice_date.year)
            MES = str(item.invoice_date.month).rjust(2, '0')
            RYF = "F1    01" if (item.move_type == "out_refund" or item.move_type == "in_refund") else "F1    01"
            E5SUJTAI = "E E5           "
            CONCEPTO = "VENTA MERCADERIAS   "
            data += FECHAFACT + " " + FECHAOP + " " + NUMFACT + " " + NUMFACR + " " + NOMBLIPROV + " " + NIF + " " + NUMSR + " " + BASE + " " + ANYO + " " + MES + " " + RYF + " " + E5SUJTAI + " " + CONCEPTO + "\n"
            item.traspasocont = True
        self.write({
            'archivo': base64.encodestring(bytes(data, "utf-8")),
            'name': "Traspaso Contable: " + str(hoy) + ".",
            'tipotraspaso': 'RECIBIDAS',
            'generaiva': True,
            'generadiario': True
        })
        return {
            'name': 'Report',
            'type': 'ir.actions.act_url',
            'url': (
                    "web/content/?model=" +
                    self._name + "&id=" + str(self.id) +
                    "&filename_field=name&field=archivo&download=true&filename=" +
                    self.name + '.txt'
            ),
            'target': '_new',
        }