# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Importación de datos de proveedores",
    "summary": "Importación de datos de proveedores",
    'version': '14.0.1.0.45',
    "category": "Project",
    "website": "www.indaws.es",
    "author": "INDAWS",
    "license": "AGPL-3",
    'application': False,
    'installable': True,
    'auto_install': False,
    "depends": [
        "sale",
        "purchase",
        "purchase_requisition",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/publish_server.xml",
        "views/purchase.xml",
        "views/schedule_test.xml",
        "views/product_template_view.xml",
        "views/product_pricelist_load_view.xml",
        "views/product_supplierinfo_view.xml",
        "views/res_partner_view.xml",
    ],
}
