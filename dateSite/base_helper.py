from datetime import datetime, date
from .models.log_session import LogSession
from .models.client import Client, Picture
from django.core.mail import EmailMessage
from django.core.serializers.base import Serializer as BaseSerializer
from django.core.serializers.python import Serializer as PythonSerializer
from django.core.serializers.json import Serializer as JsonSerializer
from django.template.loader import render_to_string
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


def get_current_client(request):
    try:
        client = Client.objects.get(clicode=request.user.pk)
        return client
    except (KeyError, Client.DoesNotExist):
        return


class ExtBaseSerializer(BaseSerializer):

    def serialize_property(self, obj):
        model = type(obj)
        for field in self.selected_fields:
            if (hasattr(model, field) and
                    type(getattr(model, field)) == property):
                self.handle_prop(obj, field)

    def handle_prop(self, obj, field):
        self._current[field] = getattr(obj, field)

    def end_object(self, obj):
        self.serialize_property(obj)

        super(ExtBaseSerializer, self).end_object(obj)


class ExtPythonSerializer(ExtBaseSerializer, PythonSerializer):
    pass


class ExtJsonSerializer(ExtPythonSerializer, JsonSerializer):
    pass


def convert_data_to_serielize(o):
    if isinstance(o, datetime) or isinstance(o, date):
        return o.__str__()
    if isinstance(o, Picture):
        return o.__str__()


# Save user log in DB. Login false is a Logout
def save_log(login, client):
    if login:
        previous_log = LogSession.objects.filter(
            clicode=client, logsignout__isnull=True)
        if previous_log:
            previous_log = LogSession.objects.filter(
                clicode=client).latest(
                'logsignin')
            previous_log.logsignout = datetime.now().isoformat()
            previous_log.save()
        client_log = LogSession()
        client_log.clicode = client
        client_log.logsignin = datetime.now().isoformat()
        client_log.save()

    else:
        previous_log = LogSession.objects.filter(
            clicode=client,
            logsignout__isnull=True).latest(
            'logsignin')
        previous_log.logsignout = datetime.now().isoformat()
        previous_log.save()
        client.clireplychannel = None
        client.save()


def send_email(subject, email_to, body, context):
    email = MIMEMultipart(_subtype='related')
    html_content = render_to_string(body, context)
    email = EmailMessage(subject, html_content, to=[email_to])
    email.content_subtype = "html"  # Main content is now text/html
    email.send()


def email_embed_image(email, img_content_id, img_data):
    img = MIMEImage(img_data)
    img.add_header('Content-ID', '<%s>' % img_content_id)
    img.add_header('Content-Disposition', 'inline')
    email.attach(img)
