import threading, os, filetype
from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings
from django.utils import timezone
from emails.models import Attachment, Email


class EmailThread(threading.Thread):
    def __init__(
        self,
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently,
        html_message,
        save=True,
        **kwargs
    ):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        self.from_email = from_email
        self.fail_silently = fail_silently
        self.html_message = html_message
        self.save=save,
        self.kwargs = kwargs
        threading.Thread.__init__(self)

    def run(self):
        connection = get_connection(**self.get_connection_data())

        # pop files first, files is a list of file objects
        attachment_files = self.kwargs.pop("files", []) or []

        if self.save:
            self.save_record(attachments=attachment_files)
        else:
            msg = EmailMultiAlternatives(
                subject=self.subject,
                body=self.message,
                from_email=self.from_email or self.get_default_from_email(),
                to=self.recipient_list,
                connection=connection,
                **self.kwargs
            )
            msg.attach_alternative(self.html_message, "text/html")
            # attach the files.
            for file in attachment_files:
                msg.attach(
                    filename=os.path.basename(file.name),
                    content=file.read(),
                    mimetype=filetype.guess_mime(file.read()),
                )
            msg.send(self.fail_silently)


    def get_connection_data(self):
        connection_data = {
            "host": settings.EMAIL_HOST,
            "port": settings.EMAIL_PORT,
            "username": settings.EMAIL_HOST_USER,
            "password": settings.EMAIL_HOST_PASSWORD,
            "use_tls": settings.EMAIL_USE_TLS,
        }
        return connection_data

    def get_default_from_email(self):
        return settings.DEFAULT_FROM_EMAIL

    def save_record(self, attachments):
        # save the mail
        attachment_objs = []
        for file in attachments:
            attachment_objs.append(Attachment.objects.create(file=file))
        
        email_obj = Email.objects.create(
            subject=self.subject,
            body=self.message,
            recipients=self.recipient_list,
            from_email=self.from_email or self.get_default_from_email(),
            cc=self.kwargs.get('cc'),
        )
        
        email_obj.send_time = timezone.now()
        email_obj.attachments.set(attachment_objs)
        email_obj.save()
