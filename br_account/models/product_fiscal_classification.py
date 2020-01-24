# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from .cst import CST_IPI


class ProductFiscalClassification(models.Model):
    _name = 'product.fiscal.classification'
    _description = 'Classificações Fiscais (NCM)'

    code = fields.Char(string="Código", size=14)
    category = fields.Char(string="Categoria", size=14)
    name = fields.Char(string="Nome", size=300)
    company_id = fields.Many2one('res.company', string="Empresa")
    unidade_tributacao = fields.Char(string="Unidade Tributável", size=4)
    descricao_unidade = fields.Char(string="Descrição Unidade", size=20)
    cest = fields.Char(string="CEST", size=10,
                       help="Código Especificador da Substituição Tributária")
    federal_nacional = fields.Float('Imposto Fed. Sobre Produto Nacional')
    federal_importado = fields.Float('Imposto Fed. Sobre Produto Importado')
    estadual_imposto = fields.Float('Imposto Estadual')
    municipal_imposto = fields.Float('Imposto Municipal')

    # IPI
    classe_enquadramento = fields.Char(string="Classe Enquadr.", size=5)
    codigo_enquadramento = fields.Char(
<<<<<<< HEAD
        string=u"Cód. Enquadramento", size=3, default='999')
    tax_ipi_id = fields.Many2one(
        comodel_name='account.tax',
        string=u"Alíquota IPI",
=======
        string="Cód. Enquadramento", size=3, default='999')
    tax_ipi_id = fields.Many2one(
        comodel_name='account.tax',
        string="Alíquota IPI",
>>>>>>> 2614df42964d4858c2816b3e0adb82b10261ed30
        domain=[('domain', '=', 'ipi')])
    ipi_tipo = fields.Selection(
        [('percent', 'Percentual')],
        string='Tipo do IPI',
        required=True,
        default='percent')
    ipi_reducao_bc = fields.Float(
<<<<<<< HEAD
        string=u'% Redução Base',
        required=True,
<<<<<<< HEAD
        digits=('Account'),
=======
        digits=dp.get_precision('Account'),
>>>>>>> f0f4466b... Atualização da tabela de NCM
=======
        string='% Redução Base',
        required=True,
        digits=('Account'),
>>>>>>> 2614df42964d4858c2816b3e0adb82b10261ed30
        default=0.00)
    ipi_cst = fields.Selection(CST_IPI, string='CST IPI')

    # ICMS ST
    tax_icms_st_id = fields.Many2one(
        comodel_name='account.tax',
<<<<<<< HEAD
        string=u"Alíquota ICMS ST",
        domain=[('domain', '=', 'icmsst')])
    icms_st_aliquota_reducao_base = fields.Float(
        string='% Red. Base ST',
<<<<<<< HEAD
        digits=('Discount'))
    icms_st_aliquota_mva = fields.Float(
        string='MVA Ajustado ST',
        digits=('Discount'), default=0.00)
=======
        digits=dp.get_precision('Discount'))
    icms_st_aliquota_mva = fields.Float(
        string='MVA Ajustado ST',
        digits=dp.get_precision('Discount'), default=0.00)
>>>>>>> f0f4466b... Atualização da tabela de NCM
=======
        string="Alíquota ICMS ST",
        domain=[('domain', '=', 'icmsst')])
    icms_st_aliquota_reducao_base = fields.Float(
        string='% Red. Base ST',
        digits=('Discount'))
    icms_st_aliquota_mva = fields.Float(
        string='MVA Ajustado ST',
        digits=('Discount'), default=0.00)
>>>>>>> 2614df42964d4858c2816b3e0adb82b10261ed30
    active = fields.Boolean(default=True, string='Ativo')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('code', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s - %s" % (rec.code, rec.name or '')))
        return result
