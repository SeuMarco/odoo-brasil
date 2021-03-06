# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

STATE = {'edit': [('readonly', False)]}


class InvoiceEletronicItem(models.Model):
    _inherit = "invoice.eletronic.item"

    @api.depends('icms_cst', 'origem')
    def _compute_cst_danfe(self):
        for item in self:
            item.cst_danfe = (item.origem or '') + (item.icms_cst or '')

    cst_danfe = fields.Char(string="CST Danfe", compute="_compute_cst_danfe")

    cest = fields.Char(string="CEST", size=10, readonly=True, states=STATE,
                       help="Código Especificador da Substituição Tributária")
    classe_enquadramento_ipi = fields.Char(
        string="Classe Enquadramento", size=5, readonly=True, states=STATE)
    codigo_enquadramento_ipi = fields.Char(
        string="Classe Enquadramento", size=3, default='999',
        readonly=True, states=STATE)

    import_declaration_ids = fields.One2many(
        'br_account.import.declaration',
        'invoice_eletronic_line_id', string='Declaração de Importação')

    # ----------- ICMS INTERESTADUAL -----------
    tem_difal = fields.Boolean(string='Difal?', readonly=True, states=STATE)
    icms_bc_uf_dest = fields.Monetary(
        string='Base ICMS', readonly=True, states=STATE)
    icms_aliquota_fcp_uf_dest = fields.Float(
        string='% FCP', readonly=True, states=STATE)
    icms_aliquota_uf_dest = fields.Float(
        string='% ICMS destino', readonly=True, states=STATE)
    icms_aliquota_interestadual = fields.Float(
        string="% ICMS Inter", readonly=True, states=STATE)
    icms_aliquota_inter_part = fields.Float(
        string='% Partilha', default=100.0, readonly=True, states=STATE)
    icms_uf_remet = fields.Monetary(
        string='ICMS Remetente', readonly=True, states=STATE)
    icms_uf_dest = fields.Monetary(
        string='ICMS Destino', readonly=True, states=STATE)
    icms_fcp_uf_dest = fields.Monetary(
        string='Valor FCP', readonly=True, states=STATE)
    informacao_adicional = fields.Text(string="Informação Adicional")
