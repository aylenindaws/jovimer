# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'

    traspasocont = fields.Boolean('Traspasado Contabilidad')
    otras_facturas = fields.Boolean('Otras facturas', related="journal_id.otras_facturas", store=True)
    journal_ids = fields.Many2many('account.journal', string='Diarios', compute='_compute_journal')

    def _get_default_journal_otras_facturas(self):
        return self.env['account.journal'].search([('otras_facturas', '=', True)], limit=1)

    journal_otras_facturas_id = fields.Many2one('account.journal', string='Diario', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 check_company=True, domain="[('id', 'in', journal_ids)]",
                                 default=_get_default_journal_otras_facturas)


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

    @api.depends('name')
    def _compute_journal(self):
        for move in self:
            move.journal_ids = self.env['account.journal'].search([('otras_facturas', '=', True)])

    @api.onchange('journal_otras_facturas_id')
    def _onchenge_journal_otras_facturas_id(self):
        if self.journal_otras_facturas_id:
            self.journal_id = self.journal_otras_facturas_id
        else:
            self.journal_id = None

    @api.depends('company_id', 'invoice_filter_type_domain')
    def _compute_suitable_journal_ids(self):
        for m in self:
            journal_type = m.invoice_filter_type_domain or 'general'
            company_id = m.company_id.id or self.env.company.id
            domain = [('company_id', '=', company_id), ('type', '=', journal_type), ('otras_facturas', '=', False)]
            m.suitable_journal_ids = self.env['account.journal'].search(domain)

