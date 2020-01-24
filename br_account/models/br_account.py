# © 2009 Renato Lima - Akretion
# © 2014  KMEE - www.kmee.com.br
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.addons.br_base.tools import fiscal
from odoo.exceptions import UserError


class BrAccountCFOP(models.Model):
    """CFOP - Código Fiscal de Operações e Prestações"""
    _name = 'br_account.cfop'
    _description = 'CFOP'

    code = fields.Char('Código', size=4, required=True)
    name = fields.Char('Nome', size=256, required=True)
    small_name = fields.Char('Nome Reduzido', size=32, required=True)
    description = fields.Text('Descrição')
    type = fields.Selection([('input', 'Entrada'), ('output', 'Saída')],
                            'Tipo',
                            required=True)
    parent_id = fields.Many2one('br_account.cfop', 'CFOP Pai')
    child_ids = fields.One2many('br_account.cfop', 'parent_id', 'CFOP Filhos')
    internal_type = fields.Selection([('view', 'Visualização'),
                                      ('normal', 'Normal')],
                                     'Tipo Interno',
                                     required=True,
                                     default='normal')

    _sql_constraints = [('br_account_cfop_code_uniq', 'unique (code)',
                         'Já existe um CFOP com esse código !')]

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


class BrAccountServiceType(models.Model):
    _name = 'br_account.service.type'
    _description = _("Cadastro de Operações Fiscais de Serviço")

    code = fields.Char(_("Código"), size=16, required=True)
    name = fields.Char(_("Descrição"), size=256, required=True)
    parent_id = fields.Many2one('br_account.service.type',
                                _("Tipo de Serviço Pai"))
    child_ids = fields.One2many('br_account.service.type', 'parent_id',
                                _("Tipo de Serviço Filhos"))
    internal_type = fields.Selection([('view', _("Visualização")),
                                      ('normal', _("Normal"))],
                                     _("Tipo Interno"),
                                     required=True,
                                     default='normal')
    federal_nacional = fields.Float(_("Imposto Fed. Sobre Serviço Nacional"))
    federal_importado = fields.Float(
        _("Imposto Fed. Sobre Serviço Importado", ))
    estadual_imposto = fields.Float(_("Imposto Estadual"))
    municipal_imposto = fields.Float(_("Imposto Municipal"))

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


class BrAccountFiscalDocument(models.Model):
    _name = 'br_account.fiscal.document'
    _description = _("Tipo de Documento Fiscal")

    code = fields.Char(_("Codigo"), size=8, required=True)
    name = fields.Char(_("Descrição"), size=64)
    electronic = fields.Boolean(_("Eletrônico"))
    nfse_eletronic = fields.Boolean(_("Emite NFS-e?"))


class BrAccountDocumentSerie(models.Model):
    _name = 'br_account.document.serie'
    _description = _("Série de documentos fiscais")

    code = fields.Char(_("Código"), size=3, required=True)
    name = fields.Char(_("Descrição"), required=True)
    active = fields.Boolean(_("Ativo"))
    fiscal_type = fields.Selection([('service', _("Serviço")),
                                    ('product', _("Produto"))],
                                   _("Tipo Fiscal"),
                                   default='service')
    fiscal_document_id = fields.Many2one('br_account.fiscal.document',
                                         _("Documento Fiscal"),
                                         required=True)
    company_id = fields.Many2one('res.company', _("Empresa"), required=True)
    internal_sequence_id = fields.Many2one('ir.sequence',
                                           _("Sequência Interna"))

    @api.model
    def _create_sequence(self, vals):
        """ Create new no_gap entry sequence for every
         new document serie """
        seq = {
            'name': vals['name'],
            'implementation': 'no_gap',
            'padding': 1,
            'number_increment': 1
        }

        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']

        return self.env['ir.sequence'].create(seq).id

    @api.model
    def create(self, vals):
        """ Overwrite method to create a new ir.sequence if
         this field is null """

        if not vals.get('internal_sequence_id'):
            vals.update({'internal_sequence_id': self._create_sequence(vals)})

        return super(BrAccountDocumentSerie, self).create(vals)


class BrAccountCNAE(models.Model):
    _name = 'br_account.cnae'
    _description = _("Cadastro de CNAE")

    code = fields.Char(_("Código"), size=16, required=True)
    name = fields.Char(_("Descrição"), size=64, required=True)
    version = fields.Char(_("Versão"), size=16, required=True)
    parent_id = fields.Many2one('br_account.cnae', _("CNAE Pai"))
    child_ids = fields.One2many('br_account.cnae', 'parent_id',
                                _("CNAEs Filhos"))
    internal_type = fields.Selection([('view', _("Visualização")),
                                      ('normal', _("Normal"))],
                                     _("Tipo Interno"),
                                     required=True,
                                     default='normal')

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


class ImportDeclaration(models.Model):
    _name = 'br_account.import.declaration'
    _description = "Declaração de Importação"

    invoice_id = fields.Many2one('account.move',
                                 _("Fatura"),
                                 ondelete='cascade',
                                 index=True)

    name = fields.Char('Número da DI', size=10, required=True)
    date_registration = fields.Date('Data de Registro', required=True)
    state_id = fields.Many2one('res.country.state',
                               'Estado',
                               domain="[('country_id.code', '=', 'BR')]",
                               required=True)
    location = fields.Char('Local', required=True, size=60)
    date_release = fields.Date('Data de Liberação', required=True)
    type_transportation = fields.Selection([
        ('1', '1 - Marítima'),
        ('2', '2 - Fluvial'),
        ('3', '3 - Lacustre'),
        ('4', '4 - Aérea'),
        ('5', '5 - Postal'),
        ('6', '6 - Ferroviária'),
        ('7', '7 - Rodoviária'),
        ('8', '8 - Conduto / Rede Transmissão'),
        ('9', '9 - Meios Próprios'),
        ('10', '10 - Entrada / Saída ficta'),
    ],
        'Transporte Internacional',
        required=True,
        default="1")
    afrmm_value = fields.Float('Valor da AFRMM',
                               digits=('Account'),
                               default=0.00)
    type_import = fields.Selection([
        ('1', '1 - Importação por conta própria'),
        ('2', '2 - Importação por conta e ordem'),
        ('3', '3 - Importação por encomenda'),
    ],
        'Tipo de Importação',
        default='1',
        required=True)
    thirdparty_cnpj = fields.Char('CNPJ', size=18)
    thirdparty_state_id = fields.Many2one(
        'res.country.state',
        'Estado',
        domain="[('country_id.code', '=', 'BR')]")
    exporting_code = fields.Char('Código do Exportador',
                                 required=True,
                                 size=60)
    line_ids = fields.One2many('br_account.import.declaration.line',
                               'import_declaration_id', 'Linhas da DI')


class ImportDeclarationLine(models.Model):
    _name = 'br_account.import.declaration.line'
    _description = "Linha da declaração de importação"

    import_declaration_id = fields.Many2one('br_account.import.declaration',
                                            'DI',
                                            ondelete='cascade')
    sequence = fields.Integer('Sequência', default=1, required=True)
    name = fields.Char('Adição', size=3, required=True)
    manufacturer_code = fields.Char('Código do Fabricante',
                                    size=60,
                                    required=True)
    amount_discount = fields.Float(string='Valor',
                                   digits=('Account'),
                                   default=0.00)
    drawback_number = fields.Char('Número Drawback', size=11)


class AccountDocumentRelated(models.Model):
    _name = 'br_account.document.related'
    _description = _("Documentos Relacionados")

    move_id = fields.Many2one('account.move',
                              _("Documento Fiscal"),
                              ondelete='cascade')
    invoice_related_id = fields.Many2one('account.move',
                                         _("Documento Fiscal"),
                                         ondelete='cascade')
    document_type = fields.Selection([('nf', _("NF")), ('nfe', _("NF-e")),
                                      ('cte', _("CT-e")),
                                      ('nfrural', _("NF Produtor")),
                                      ('cf', _("Cupom Fiscal"))],
                                     _("Tipo Documento"),
                                     required=True)
    access_key = fields.Char(_("Chave de Acesso"), size=44)
    serie = fields.Char(_("Série"), size=12)
    internal_number = fields.Char(_("Número"), size=32)
    state_id = fields.Many2one('res.country.state',
                               _("Estado"),
                               domain="[('country_id.code', '=', 'BR')]")
    cnpj_cpf = fields.Char(_("CNPJ/CPF"), size=18)
    cpfcnpj_type = fields.Selection([('cpf', 'CPF'), ('cnpj', 'CNPJ')],
                                    _("Tipo Doc."),
                                    default='cnpj')
    inscr_est = fields.Char(_("Inscr. Estadual/RG"), size=16)
    date = fields.Date(_("Data"))
    fiscal_document_id = fields.Many2one('br_account.fiscal.document',
                                         _("Documento"))

    @api.constrains('cnpj_cpf')
    def _check_cnpj_cpf(self):
        check_cnpj_cpf = True

        for rec in self:
            if rec.cnpj_cpf:
                if rec.cpfcnpj_type == 'cnpj':
                    if not fiscal.validate_cnpj(rec.cnpj_cpf):
                        check_cnpj_cpf = False
                elif not fiscal.validate_cpf(rec.cnpj_cpf):
                    check_cnpj_cpf = False

            if not check_cnpj_cpf:
                raise UserError(
                    _('CNPJ/CPF do documento relacionado é invalido!', ))

    @api.constrains('inscr_est')
    def _check_ie(self):
        check_ie = True

        if self.inscr_est:
            uf = self.state_id and self.state_id.code.lower() or ''
            try:
                mod = __import__('odoo.addons.br_base.tools.fiscal', globals(),
                                 locals(), 'fiscal')

                validate = getattr(mod, 'validate_ie_%s' % uf)

                if not validate(self.inscr_est):
                    check_ie = False
            except AttributeError:
                if not fiscal.validate_ie_param(uf, self.inscr_est):
                    check_ie = False

        if not check_ie:
            raise UserError(
                _('Inscrição Estadual do documento fiscal inválida!'))

    @api.onchange('invoice_related_id')
    def onchange_invoice_related_id(self):
        if not self.invoice_related_id:
            return
        inv_id = self.invoice_related_id

        if not inv_id.product_document_id:
            return

        self.document_type = \
            self.translate_document_type(inv_id.product_document_id.code)

        if inv_id.product_document_id.code in ('55', '57'):
            self.serie = False
            self.internal_number = False
            self.state_id = False
            self.cnpj_cpf = False
            self.cpfcnpj_type = False
            self.date = False
            self.fiscal_document_id = False
            self.inscr_est = False

    def translate_document_type(self, code):
        if code == '55':
            return 'nfe'
        elif code == '04':
            return 'nfrural'
        elif code == '57':
            return 'cte'
        elif code in ('2B', '2C', '2D'):
            return 'cf'
        else:
            return 'nf'


class BrAccountFiscalObservation(models.Model):
    _name = 'br_account.fiscal.observation'
    _description = _("Mensagen Documento Eletrônico")
    _order = 'sequence'

    sequence = fields.Integer(_("Sequência"), default=1, required=True)
    name = fields.Char(_("Descrição"), required=True, size=50)
    message = fields.Text(_("Mensagem"), required=True)
    tipo = fields.Selection([('fiscal', _("Observação Fiscal")),
                             ('observacao', _("Observação"))],
                            string=_("Tipo"))
    document_id = fields.Many2one('br_account.fiscal.document',
                                  string=_("Documento Fiscal"))


class BrAccountCategoriaFiscal(models.Model):
    _name = 'br_account.fiscal.category'
    _description = _("Categoria Fiscal")

    name = fields.Char(_("Descrição"), required=True)
