# -*- coding: utf-8 -*-
{
    "name": "Account extend Jovimer",

    'summary': """
        Perosnalizacion JOVIMER Procesos de contabilidad
    """,

    'description': """
        Perosnalizacion JOVIMER Procesos de contabilidad
    """,

    'author': "Indaws",
    'website': "https://www.indaws.es/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0.4',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_accountant', 'indaws_product_extended'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        "data/cron.xml",
        'views/jovimer_traspasoconta_view.xml',
        'views/jovimer_traspasocyp_view.xml',
        # 'views/account_move_view.xml',
        'views/account_journal_view.xml',
        'views/otras_facturas_view.xml',
    ],
    "images": ["static/description/icon.png"],
    "application": True,
    "auto_install": False,
    "installable": True,
    "currency": "EUR"
}
