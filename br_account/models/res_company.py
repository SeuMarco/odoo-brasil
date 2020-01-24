# © 2009 Renato Lima - Akretion
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields

COMPANY_FISCAL_TYPE = [
    ('1', 'Simples Nacional'),
    ('2', 'Simples Nacional – excesso de sublimite de receita bruta'),
    ('3', 'Regime Normal')
]

COMPANY_FISCAL_TYPE_DEFAULT = '3'


class ResCompany(models.Model):
    _inherit = 'res.company'

    fiscal_document_for_product_id = fields.Many2one(
        'br_account.fiscal.document', "Documento Fiscal para produto")

    annual_revenue = fields.Float(
        'Faturamento Anual', required=True,
<<<<<<< HEAD
<<<<<<< HEAD
        digits=dp.get_precision('Account'), default=0.00,
        help=u"Faturamento Bruto dos últimos 12 meses")
=======
        digits=('Account'), default=0.00,
        help="Faturamento Bruto dos últimos 12 meses")
>>>>>>> 2614df42... A pasos agigantados
=======
        digits=('Account'), default=0.00,
        help="Faturamento Bruto dos últimos 12 meses")
>>>>>>> 2614df42964d4858c2816b3e0adb82b10261ed30
    fiscal_type = fields.Selection(
        COMPANY_FISCAL_TYPE, 'Regime Tributário', required=True,
        default=COMPANY_FISCAL_TYPE_DEFAULT)
    cnae_main_id = fields.Many2one(
        'br_account.cnae', 'CNAE Primário')
    cnae_secondary_ids = fields.Many2many(
        'br_account.cnae', 'res_company_br_account_cnae',
        'company_id', 'cnae_id', 'CNAE Secundários')

    accountant_id = fields.Many2one('res.partner', string="Contador")
