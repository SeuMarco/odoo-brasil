# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models
from odoo.addons.br_account.models.cst import CST_ICMS
from odoo.addons.br_account.models.cst import CSOSN_SIMPLES
from odoo.addons.br_account.models.cst import CST_IPI
from odoo.addons.br_account.models.cst import CST_PIS_COFINS


class AccountFiscalPositionTaxRule(models.Model):
    _name = 'account.fiscal.position.tax.rule'
    _order = 'sequence'

    sequence = fields.Integer(string="Sequência")
    name = fields.Char(string="Descrição", size=100)
    domain = fields.Selection([('icms', 'ICMS'),
                               ('pis', 'PIS'),
                               ('cofins', 'COFINS'),
                               ('ipi', 'IPI'),
                               ('issqn', 'ISSQN'),
                               ('ii', 'II'),
                               ('csll', 'CSLL'),
                               ('irrf', 'IRRF'),
                               ('inss', 'INSS'),
                               ('outros', 'Outros')], string="Tipo")
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position', string="Posição Fiscal")

    state_ids = fields.Many2many('res.country.state', string="Estado Destino",
                                 domain=[('country_id.code', '=', 'BR')])
    fiscal_category_ids = fields.Many2many(
        'br_account.fiscal.category', string="Categorias Fiscais")
    tipo_produto = fields.Selection([('product', 'Produto'),
                                     ('service', 'Serviço')],
                                    string="Tipo produto", default="product")

    product_fiscal_classification_ids = fields.Many2many(
        'product.fiscal.classification', string="Classificação Fiscal",
        relation="account_fiscal_position_tax_rule_prod_fiscal_clas_relation")

    cst_icms = fields.Selection(CST_ICMS, string="CST ICMS")
    csosn_icms = fields.Selection(CSOSN_SIMPLES, string="CSOSN ICMS")
    cst_pis = fields.Selection(CST_PIS_COFINS, string="CST PIS")
    cst_cofins = fields.Selection(CST_PIS_COFINS, string="CST COFINS")
    cst_ipi = fields.Selection(CST_IPI, string="CST IPI")
    cfop_id = fields.Many2one('br_account.cfop', string="CFOP")
    tax_id = fields.Many2one('account.tax', string="Imposto")
    tax_icms_st_id = fields.Many2one('account.tax', string="ICMS ST",
                                     domain=[('domain', '=', 'icmsst')])
    icms_aliquota_credito = fields.Float(string="% Crédito de ICMS")
    incluir_ipi_base = fields.Boolean(string="Incl. IPI na base ICMS")
    reducao_icms = fields.Float(string="Redução de base")
    reducao_icms_st = fields.Float(string="Redução de base ST")
    reducao_ipi = fields.Float(string="Redução de base IPI")
    aliquota_mva = fields.Float(string="Alíquota MVA")
    icms_st_aliquota_deducao = fields.Float(
        string="% ICMS Próprio",
        help="Alíquota interna ou interestadual aplicada \
         sobre o valor da operação para deduzir do ICMS ST - Para empresas \
         do Simples Nacional ou usado em casos onde existe apenas ST sem ICMS")
    tem_difal = fields.Boolean(string="Aplicar Difal?")
    tax_icms_inter_id = fields.Many2one(
        'account.tax', help="Alíquota utilizada na operação Interestadual",
        string="ICMS Inter", domain=[('domain', '=', 'icms_inter')])
    tax_icms_intra_id = fields.Many2one(
        'account.tax', help="Alíquota interna do produto no estado destino",
        string="ICMS Intra", domain=[('domain', '=', 'icms_intra')])
    tax_icms_fcp_id = fields.Many2one(
        'account.tax', string="% FCP", domain=[('domain', '=', 'fcp')])


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    journal_id = fields.Many2one(
        'account.journal', string="Diário Contábil",
        help="Diário Contábil a ser utilizado na fatura.")
    account_id = fields.Many2one(
        'account.account', string="Conta Contábil",
        help="Conta Contábil a ser utilizada na fatura.")
    fiscal_observation_ids = fields.Many2many(
        'br_account.fiscal.observation', string="Mensagens Doc. Eletrônico")
    note = fields.Text('Observações')

    product_serie_id = fields.Many2one(
        'br_account.document.serie', string='Série Produto',
        domain="[('fiscal_document_id', '=', product_document_id)]")
    product_document_id = fields.Many2one(
        'br_account.fiscal.document', string='Documento Produto')

    service_serie_id = fields.Many2one(
        'br_account.document.serie', string='Série Serviço',
        domain="[('fiscal_document_id', '=', service_document_id)]")
    service_document_id = fields.Many2one(
        'br_account.fiscal.document', string='Documento Serviço')

    icms_tax_rule_ids = fields.One2many(
        'account.fiscal.position.tax.rule', 'fiscal_position_id',
        string="Regras ICMS", domain=[('domain', '=', 'icms')])
    ipi_tax_rule_ids = fields.One2many(
        'account.fiscal.position.tax.rule', 'fiscal_position_id',
        string="Regras IPI", domain=[('domain', '=', 'ipi')])
    pis_tax_rule_ids = fields.One2many(
        'account.fiscal.position.tax.rule', 'fiscal_position_id',
        string="Regras PIS", domain=[('domain', '=', 'pis')])
    cofins_tax_rule_ids = fields.One2many(
        'account.fiscal.position.tax.rule', 'fiscal_position_id',
        string="Regras COFINS", domain=[('domain', '=', 'cofins')])
    issqn_tax_rule_ids = fields.One2many(
        'account.fiscal.position.tax.rule', 'fiscal_position_id',
        string="Regras ISSQN", domain=[('domain', '=', 'issqn')])
    ii_tax_rule_ids = fields.One2many(
        'account.fiscal.position.tax.rule', 'fiscal_position_id',
        string="Regras II", domain=[('domain', '=', 'ii')])
    irrf_tax_rule_ids = fields.One2many(
        'account.fiscal.position.tax.rule', 'fiscal_position_id',
        string="Regras IRRF", domain=[('domain', '=', 'irrf')])
    csll_tax_rule_ids = fields.One2many(
        'account.fiscal.position.tax.rule', 'fiscal_position_id',
        string="Regras CSLL", domain=[('domain', '=', 'csll')])
    inss_tax_rule_ids = fields.One2many(
        'account.fiscal.position.tax.rule', 'fiscal_position_id',
        string="Regras INSS", domain=[('domain', '=', 'inss')])
    fiscal_type = fields.Selection([('saida', 'Saída'),
                                    ('entrada', 'Entrada')],
                                   string="Tipo da posição")

    @api.model
    def _get_fpos_by_region(self, country_id=False, state_id=False,
                            zipcode=False, vat_required=False):
        fpos = super(AccountFiscalPosition, self)._get_fpos_by_region(
            country_id=country_id, state_id=state_id, zipcode=zipcode,
            vat_required=vat_required)
        type_inv = self.env.context.get('type', False)
        supplier = self.env.context.get('search_default_supplier', False)
        customer = self.env.context.get('search_default_customer', False)
        if type_inv == 'in_invoice' or supplier:
            type_inv = 'entrada'
        elif type_inv == 'out_invoice' or customer:
            type_inv = 'saida'
        fpos = self.search([('auto_apply', '=', True),
                            ('fiscal_type', '=', type_inv)], limit=1)
        return fpos

    def _filter_rules(self, fpos_id, type_tax, partner, product, state):
        rule_obj = self.env['account.fiscal.position.tax.rule']
        domain = [('fiscal_position_id', '=', fpos_id),
                  ('domain', '=', type_tax)]
        rules = rule_obj.search(domain)
        if rules:
            rules_points = {}
            for rule in rules:

                # Calcula a pontuacao da regra.
                # Quanto mais alto, mais adequada está a regra em relacao ao
                # faturamento
                rules_points[rule.id] = self._calculate_points(
                    rule, product, state, partner)

            # Calcula o maior valor para os resultados obtidos
            greater_rule = max([(v, k) for k, v in list(rules_points.items())])
            # Se o valor da regra for menor do que 0, a regra é descartada.
            if greater_rule[0] < 0:
                return {}

            # Procura pela regra associada ao id -> (greater_rule[1])
            rules = [rules.browse(greater_rule[1])]

            # Retorna dicionario com o valores dos campos de acordo com a regra
            return {
                ('%s_rule_id' % type_tax): rules[0],
                'cfop_id': rules[0].cfop_id,
                ('tax_%s_id' % type_tax): rules[0].tax_id,
                # ICMS
                'icms_cst_normal': rules[0].cst_icms,
                'icms_aliquota_reducao_base': rules[0].reducao_icms,
                'incluir_ipi_base': rules[0].incluir_ipi_base,
                # ICMS ST
                'tax_icms_st_id': rules[0].tax_icms_st_id,
                'icms_st_aliquota_mva': rules[0].aliquota_mva,
                'icms_st_aliquota_reducao_base': rules[0].reducao_icms_st,
                'icms_st_aliquota_deducao': rules[0].icms_st_aliquota_deducao,
                # ICMS Difal
                'tem_difal': rules[0].tem_difal,
                'tax_icms_inter_id': rules[0].tax_icms_inter_id,
                'tax_icms_intra_id': rules[0].tax_icms_intra_id,
                'tax_icms_fcp_id': rules[0].tax_icms_fcp_id,
                # Simples
                'icms_csosn_simples': rules[0].csosn_icms,
                'icms_aliquota_credito': rules[0].icms_aliquota_credito,
                # IPI
                'ipi_cst': rules[0].cst_ipi,
                'ipi_reducao_bc': rules[0].reducao_ipi,
                # PIS
                'pis_cst': rules[0].cst_pis,
                # PIS
                'cofins_cst': rules[0].cst_cofins,
            }
        else:
            return{}

    @api.model
    def map_tax_extra_values(self, company, product, partner):
        to_state = partner.state_id

        taxes = ('icms', 'simples', 'ipi', 'pis', 'cofins',
                 'issqn', 'ii', 'irrf', 'csll', 'inss')
        res = {}
        for tax in taxes:
            vals = self._filter_rules(
                self.id, tax, partner, product, to_state)
            res.update({k: v for k, v in list(vals.items()) if v})
        return res

    def _calculate_points(self, rule, product, state, partner):
        """Calcula a pontuação das regras. A pontuação aumenta de acordo
        com os 'matches'. Não havendo match(exceto quando o campo não está
        definido) retorna o valor -1, que posteriormente será tratado como
        uma regra a ser descartada.
        """

        rule_points = 0

        # Verifica o tipo do produto. Se sim, avança para calculo da pontuação
        # Se não, retorna o valor -1 (a regra será descartada)
        if product.fiscal_type == rule.tipo_produto:

            # Verifica a categoria fiscal. Se contido, adiciona 1 ponto
            # Se não, retorna valor -1 (a regra será descartada)
            if product.fiscal_category_id in rule.fiscal_category_ids:
                rule_points += 1
            elif len(rule.fiscal_category_ids) > 0:
                return -1

            # Verifica produtos. Se contido, adiciona 1 ponto
            # Se não, retorna -1
            if product.fiscal_classification_id in\
                    rule.product_fiscal_classification_ids:
                rule_points += 1
            elif len(rule.product_fiscal_classification_ids) > 0:
                return -1

            # Verifica o estado. Se contido, adiciona 1 ponto
            # Se não, retorna -1
            if state in rule.state_ids:
                rule_points += 1
            elif len(rule.state_ids) > 0:
                return -1

        else:
            return -1

        return rule_points
