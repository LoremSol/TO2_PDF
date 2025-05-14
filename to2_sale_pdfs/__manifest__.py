# -*- coding: utf-8 -*-
{
    'name': "to2_sale_pdfs",

    'summary': "Módulo para testeo del trabajo sobre PDFs",

    'description': """
Módulo encargado de redefinir views de Sales para las pruebas con la generación y redimensión de PDFs
    """,

    'author': "TiOdoo",
    'website': "https://www.tiodoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'views/to2_sale_order_view.xml',
    ],
}

