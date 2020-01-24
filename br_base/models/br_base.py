# © 2009  Renato Lima - Akretion
# © 2015  Michell Stuttgart - KMEE
# © 2016 Danimar Ribeiro <danimaribeiro@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, models, fields


class ResStateCity(models.Model):
    """ Este objeto persite todos os municípios relacionado a um estado.
    No Brasil é necessário em alguns documentos fiscais informar o código
    do IBGE dos município envolvidos da transação.
    """
    _name = 'res.state.city'
    _description = _("City")

    name = fields.Char(string=_("Name"), size=64, required=True)
    state_id = fields.Many2one(
        comodel_name='res.country.state', string=_("State"), required=True)
    ibge_code = fields.Char(string=_("IBGE Code"), size=7, copy=False)


class ResRegion(models.Model):
    _name = 'res.region'
    _description = _("Região")

    name = fields.Char(string=_("Name"), size=100)
    city_ids = fields.Many2many('res.state.city', string=_("Cities"))
    state_ids = fields.Many2many('res.country.state', string=_("States"))
