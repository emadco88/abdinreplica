from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AbAnnouncement(models.Model):
    _name = 'ab_announcement'
    _description = 'ab_announcement'
    _inherit = ['mail.thread', 'abdin_telegram']
    _order = 'release_date desc'
    _rec_name = 'title'

    title = fields.Selection(
        selection=[('decree', 'Decree'),
                   ('notice', 'Notice'),
                   ],
        default='decree',
        required=True,
    )

    subject = fields.Text(required=True)
    subject_body = fields.Html(default=lambda self: self._get_default_subject_body())
    issuer = fields.Many2one('ab_hr_department', required=True)
    release_date = fields.Date(required=True, index=True)
    announcement_type = fields.Selection(
        selection=[('policies_and_instructions', 'Policies And Instructions'),
                   ("employees_movements", "Employees' Movements"),
                   ('notices_and_warnings', 'Notices And Warnings'),
                   ('holidays', 'Holidays')
                   ],
        default="policies_and_instructions",
        required=True,
    )
    announcement_link = fields.Char(compute='_compute_announcement_link', compute_sudo=True)

    number = fields.Char()
    attachment = fields.Binary()
    is_posted = fields.Boolean()
    send_attachment = fields.Boolean(default=True)

    @api.constrains('title', 'number', 'announcement_type')
    def _constrains_ab_announcement(self):
        for rec in self:
            if rec.title == 'decree' and not rec.number:
                raise ValidationError(_("A number is required for decree!"))
            if rec.title == 'decree' and rec.announcement_type == 'notices_and_warnings':
                raise ValidationError(_("Notices and warning is not a decree!"))
            if rec.title == 'notice' and rec.announcement_type != 'notices_and_warnings':
                raise ValidationError(_("Type must be notices and warnings."))

    def name_get(self):
        trans_mo = self.env['ir.translation'].sudo()

        res = []
        for rec in self:
            number = f"({rec.number})" if rec.title == 'decree' else ""
            announcement_type = dict(trans_mo.get_field_selection(rec._name, 'announcement_type')).get(
                rec.announcement_type)

            res.append((rec.id, f"{announcement_type} {number}"))
        return res

    def _compute_announcement_link(self):
        for rec in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            rec.announcement_link = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"

    def btn_post_telegram(self):
        trans_mo = self.env['ir.translation'].sudo()
        if not self.env.user.has_group('ab_hr.group_ab_hr_co'):
            raise ValidationError(_("Only Coordinator group can post."))

        self.is_posted = True
        subject_lines = self.subject.split('\n')
        subject = ""

        title = dict(trans_mo.get_field_selection(self._name, 'title')).get(self.title)
        fields_str = trans_mo.get_field_string(self._name)

        subject += f"<div>{fields_str['number']}: {self.number}</div>" if self.title == 'decree' else ""
        subject += f"<div>{fields_str['release_date']}: {self.release_date}</div>"
        subject += f"<div>{fields_str['issuer']}: {self.issuer.name}</div>"
        subject += "".join(f"<div>{line}</div>" for line in subject_lines if line)

        # before = f"""<b>Noted by:</b> {self.env.user.name}\n\n"""
        before = f"""<b>##### {title} #####</b>\n\n"""
        after = f"\n\n<a href='{self.announcement_link}'>Goto Announcement ⏩</a>"

        attachment = self.attachment if self.send_attachment else None

        self.send_by_bot(self.get_chat_id("telegram_announcement_group_chat_id"),
                         msg=subject,
                         before=before,
                         after=after,
                         name_ext='announcement.pdf',
                         attachment=attachment)

        title = _("Message is posted successfully on telegram.")
        status = 'success'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'type': status,
                'sticky': False,  # True/False will display for few seconds if false
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    def btn_acknowledge(self):
        partner_id = self.env.user.partner_id.id

        is_post_before = False
        for message in self.message_ids:
            if message.author_id.id == partner_id:
                is_post_before = True

        if is_post_before:
            raise ValidationError(_("You Confirm Acknowledgement before"))
        else:
            self.message_post(body="Acknowledge")

    def _get_default_subject_body(self):
        return """<h1 class='text-center'>Title</h1>
        <p>Paragraph</p>
        <footer>
        <p>Footer</p>
        </footer>
        """
