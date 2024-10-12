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
