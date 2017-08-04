from django.core.mail.backends.smtp import EmailBackend


class DevelEmailBackend(EmailBackend):
    EMAIL_WHITELIST = ('@10clouds.com')

    def _send(self, email_message):
        email_message.to = [addr for addr in email_message.to if addr.endswith(self.EMAIL_WHITELIST)]
        email_message.cc = [addr for addr in email_message.cc if addr.endswith(self.EMAIL_WHITELIST)]
        email_message.bcc = [addr for addr in email_message.bcc if addr.endswith(self.EMAIL_WHITELIST)]
        return super()._send(email_message)
