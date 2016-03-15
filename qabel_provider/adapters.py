from allauth.account.adapter import DefaultAccountAdapter


class IgnoreInvalidMailsAdapter(DefaultAccountAdapter):

    def send_mail(self, template_prefix, email, context):
        msg = self.render_mail(template_prefix, email, context)
        msg.send(fail_silently=True)
