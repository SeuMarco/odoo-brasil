# © 2019 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    senha_nfse_simpliss = fields.Char(
        string='Senha NFSe SimplISS', size=30,
<<<<<<< HEAD
<<<<<<< HEAD
        help='Senha Nota Fiscal de Serviço')
=======
        help=u'Senha Nota Fiscal de Serviço')
>>>>>>> 48ca78e2... [IMP] Implementação parcial NFSe aparecida e correçaõ NFSe Simpliss
=======
        help=u'Senha Nota Fiscal de Serviço')
>>>>>>> 2614df42964d4858c2816b3e0adb82b10261ed30
