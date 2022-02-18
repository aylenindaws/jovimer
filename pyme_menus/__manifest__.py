# -*- coding: utf-8 -*-
{
    'name': "Pyme Menús",

    'summary': """
        Creación de los menús PYME""",

    'description': """
        Gestion de Menu, Acciones y personalizaciones para: OpenERP PYME.
    """,

    'author': "MAIN INFORMÁTICA GANDIA SL",
    'website': "http://www.main-informatica.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sale', 'purchase','menupyme','purchase_order_type','sale_order_type','account_balance_line','l10n_es_vat_book','project','website_crm','backend_theme_v12','account_cancel','account_clean_cancelled_invoice_number','calendar','calendar_sms','web_tree_dynamic_colored_field','bt_account_balance_check_by_date','account_renumber','intero_reload_form','purchase_discount','base_fontawesome','purchase_order_line_description','sale_order_line_description','pyme_descuentos2'],

    # always loaded
    'data': [
        'views/productividad.xml',
        'views/mantenimiento.xml',
        'views/configuracion.xml',
		'views/tesoreria.xml',
        'views/stock_location_view.xml',
        'views/stock_quant_view.xml',
        'views/stock_move_line_view.xml',
		'views/res_partner.xml',
		'views/ventas.xml',
		'views/compras.xml',
        'data/data.xml',
        'security/ir.model.access.csv',
        'data/default_type.xml',
        'views/menus.xml',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': True,

}