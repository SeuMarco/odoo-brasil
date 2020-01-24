# © 2016 Danimar Ribeiro <danimaribeiro@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class BrAccountServiceType(models.Model):
    _inherit = 'br_account.service.type'

    codigo_tributacao_municipio = fields.Char(
<<<<<<< HEAD
<<<<<<< HEAD
        string="Cód. Tribut. Munic.", size=20,
=======
        string=u"Cód. Tribut. Munic.", size=20,
>>>>>>> 48ca78e2... [IMP] Implementação parcial NFSe aparecida e correçaõ NFSe Simpliss
=======
        string=u"Cód. Tribut. Munic.", size=20,
>>>>>>> 2614df42964d4858c2816b3e0adb82b10261ed30
        help="Código de Tributação no Munípio")
