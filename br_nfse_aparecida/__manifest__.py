# © 2019 Danimar Ribeiro <danimaribeiro@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'Envio de NFS-e Aparecida - SP',
    'summary': """Permite o envio de NFS-e Aparecida-SP nas faturas do Odoo
    Mantido por Trustcode""",
    'description': 'Envio de NFS-e - Aparecida-SP',
<<<<<<< HEAD
<<<<<<< HEAD
    'version': '13.0.1.0.0',
=======
    'version': '12.0.1.0.0',
>>>>>>> 48ca78e2... [IMP] Implementação parcial NFSe aparecida e correçaõ NFSe Simpliss
=======
    'version': '12.0.1.0.0',
>>>>>>> 2614df42964d4858c2816b3e0adb82b10261ed30
    'category': 'account',
    'author': 'Trustcode',
    'website': 'http://www.trustcode.com.br',
    'license': 'AGPL-3',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'br_nfse',
    ],
    'data': [
        'views/br_account_service.xml',
        # 'reports/danfse_ginfes.xml',
    ],
    'installable': True,
    'application': True,
}
