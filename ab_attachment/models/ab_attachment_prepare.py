from odoo import api, fields, models, _
from odoo.http import request


class AttachmentPrepare(models.AbstractModel):
    _name = 'ab_attachment_prepare'
    _description = 'ab_attachment_prepare'

    def action_download_att_ids(self, attachment_ids):
        # Convert the list of ids to a string
        request.session['attachment_ids'] = attachment_ids
        # Return an action of type 'ir.actions.act_url'
        return {
            'type': 'ir.actions.act_url',
            'url': '/attachments_download',
            'target': 'self',
        }
