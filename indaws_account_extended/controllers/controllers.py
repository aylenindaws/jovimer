# -*- coding: utf-8 -*-
# from odoo import http


# class IndawsAccountExtended(http.Controller):
#     @http.route('/indaws_account_extended/indaws_account_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/indaws_account_extended/indaws_account_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('indaws_account_extended.listing', {
#             'root': '/indaws_account_extended/indaws_account_extended',
#             'objects': http.request.env['indaws_account_extended.indaws_account_extended'].search([]),
#         })

#     @http.route('/indaws_account_extended/indaws_account_extended/objects/<model("indaws_account_extended.indaws_account_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('indaws_account_extended.object', {
#             'object': obj
#         })
