import base64
import io
import zipfile
from odoo import http


class AttachmentDownloader(http.Controller):
    @http.route('/attachments_download', type='http', auth='user')
    def download_files(self, **kw):
        # Get the attachment ids from the URL parameters
        attachment_ids = http.request.session.get('attachment_ids', [])

        # Get the attachments
        attachments = http.request.env['ir.attachment'].sudo().browse(attachment_ids)

        # Create a BytesIO object
        zip_buffer = io.BytesIO()

        # Create a ZipFile object
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for attachment in attachments:
                file_data = base64.b64decode(attachment.datas)
                file_name = f"{attachment.id}-{attachment.name}"

                # Add file to the ZipFile
                zip_file.writestr(file_name, file_data)

        # Get the value of the BytesIO buffer
        zip_buffer.seek(0)
        zip_data = zip_buffer.read()

        # Return the ZipFile as a download
        return http.request.make_response(
            zip_data,
            headers=[
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', 'attachment; filename=files.zip;')
            ]
        )
