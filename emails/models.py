from django.db import models


class Attachment(models.Model):
    file = models.FileField(upload_to='emails/attachments', max_length=500, null=True)


class Email(models.Model):
    """
    Represents an email triggered from the system
    """

    subject = models.CharField(max_length=500, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    recipients = models.JSONField(null=True, blank=True)
    from_email = models.CharField(max_length=100, null=True, blank=True)
    cc = models.JSONField(null=True, blank=True)
    attachments = models.ManyToManyField(Attachment, blank=True)
    send_time = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    status = models.CharField(max_length=50, null=True, blank=True)
    log = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def send_mail(self):
        # need to import here, otherwise circular import will happen
        from emails.utils import EmailThread

        try:
            EmailThread(
                subject=self.subject,
                from_email=self.from_email,
                recipient_list=self.recipients,
                fail_silently=True,
                message=self.body,
                html_message=self.body,
                files=[attachment.file for attachment in self.attachments.all()],
                cc=self.cc,
                save=False
            ).run()
            self.status = "SUCCESS"
        except Exception as e:
            self.log = f"Couldn't send email. Error: {e}"
            self.status = "FAILED"
        self.save()
