# -*- coding: utf-8 -*-
{
    'name': "Sale Order Availability Icon",
    'summary': """ Change Icon color in sale order product availability """,
    'description': """ Change Icon color in sale order product availability """,
    'author': "inDAWS",
    'website': "http://www.indaws.es",
    'category': 'product',
    'version': '14.0.1.0.0',
    'sequence': 1,
    'installable': True,
    'application': False,
    'auto_install': False,
    'depends': ['sale_stock'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/sale_stocks.xml',
    ],
}
