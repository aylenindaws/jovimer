# -*- coding: utf-8 -*-
from odoo import http

# class Modulo-base(http.Controller):
#     @http.route('/modulo-base/modulo-base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/modulo-base/modulo-base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('modulo-base.listing', {
#             'root': '/modulo-base/modulo-base',
#             'objects': http.request.env['modulo-base.modulo-base'].search([]),
#         })

#     @http.route('/modulo-base/modulo-base/objects/<model("modulo-base.modulo-base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('modulo-base.object', {
#             'object': obj
#         })