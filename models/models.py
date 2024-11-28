# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cwg_purchase_custom(models.Model):
#     _name = 'cwg_purchase_custom.cwg_purchase_custom'
#     _description = 'cwg_purchase_custom.cwg_purchase_custom'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

