# -*- coding: utf-8 -*-
{
    'name': "sale_custom_cost",

    'summary': """
        custmize sale with new functionality""",

    'description': """
        custmize sale with new functionality
    """,
    'author': "inDAWS",
    'website': "http://www.indaws.es",
    'category': 'sale',
    'version': '14.0.1.0.11',
    'sequence': 1,
    'installable': True,
    'application': False,
    'auto_install': False,
    'depends': ['sale_management', 'sale_margin'],
    'data': [
        'views/sale_views.xml',
        'views/sale_margin_views.xml',
    ],
}
