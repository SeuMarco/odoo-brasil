# © 2009  Renato Lima - Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'Odoo Brasil - Módulo Base',
    'description': 'Brazilian Localization Base',
    'version': '13.0.1.0.0',
    'category': 'Localization',
    'license': 'AGPL-3',
    'author': 'Akretion, OpenERP Brasil',
    'website': 'http://www.trustcode.com,br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        'Carlos Alberto Cipriano Korovsky <carlos.korovsky@uktech.com.br',
    ],
    'depends': [
        'base', 'web',
    ],
    'external_dependencies': {
        'python': [
            'pytrustnfe3',
        ],
    },
    'data': [
        'views/br_base.xml',
        'views/ir_module.xml',
        'views/br_base_view.xml',
        'views/res_country_view.xml',
        'views/res_partner_view.xml',
        'views/res_bank_view.xml',
        'views/res_company_view.xml',
        'views/base_assets.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'post_init_hook': 'post_init',
    'installable': True,
    'auto_install': True,
}
