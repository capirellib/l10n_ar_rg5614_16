from odoo import models, fields, api
import base64


class UploadCertificateWizard(models.TransientModel):
    _name = "custom_upload_certficate_wizard"
    _inerit = "afipws.upload_certificate.wizard"
    _description = "Upload Certificate Wizard"

    def action_confirm(self):
        # Decodificar el archivo de certificado
        if self.certificate_file:
            decoded_certificate = base64.b64decode(self.certificate_file)
            self.certificate_id.write({"crt": decoded_certificate})
        return True
