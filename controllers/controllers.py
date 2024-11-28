# -*- coding: utf-8 -*-
# from odoo import http


# class CwgPurchaseCustom(http.Controller):
#     @http.route('/cwg_purchase_custom/cwg_purchase_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cwg_purchase_custom/cwg_purchase_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cwg_purchase_custom.listing', {
#             'root': '/cwg_purchase_custom/cwg_purchase_custom',
#             'objects': http.request.env['cwg_purchase_custom.cwg_purchase_custom'].search([]),
#         })

#     @http.route('/cwg_purchase_custom/cwg_purchase_custom/objects/<model("cwg_purchase_custom.cwg_purchase_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cwg_purchase_custom.object', {
#             'object': obj
#         })

