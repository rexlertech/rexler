import json
import random
from datetime import datetime, date
from .context_processor import *
from django.http import JsonResponse
from django.http import HttpResponse
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms import formset_factory
from django.shortcuts import (render, redirect, render_to_response,
                              get_object_or_404)
from django.contrib.auth.decorators import login_required

from allauth.account.views import (SignupView, LoginView, PasswordResetView,
                                   LogoutView)

from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from dateutil.relativedelta import relativedelta

from .models.testimonial import Testimonial
from .models.client import (Client, Picture, PhotoAlbum, ManagerClient,
                            ClientCollectionAlbum)
from .models.catalog import Gender, Feeling, TypeClient, City, Country
from .models.notification import Notification, NotificationType
from .models.log_session import LogSession
from .models.purchase import Record, Purchase

from .base_helper import (ExtJsonSerializer, convert_data_to_serielize,
                          save_log, send_email)
from .forms import (LoginForm, GoodLuckSearchForm, ResetPasswordForm,
                    SignupForm, EditProfileForm, UploadAlbumForm,
                    FullSearchForm)
from channels import Channel
from .ajax_request import *


class LoginView(LoginView):

    def __init__(self, **kwargs):
        super(LoginView, self).__init__(*kwargs)

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        client_testimonials = list(Testimonial.objects.filter(
            testype='C',
            tesactive=True).order_by(
            '-tesname')[:6])
        context['client_testimonials'] = client_testimonials
        love_stories = list(Testimonial.objects.filter(
            testype='L',
            tesactive=True).order_by(
            '-tesname')[:6])
        context['love_stories'] = love_stories
        # Cantidad de miembros
        context['total_members'] = Client.total_members()
        context['total_women'] = Client.total_members_by_gender(2)
        context['total_men'] = Client.total_members_by_gender(1)
        context['total_online'] = Client.total_members_online()
        return context

    def form_invalid(self, form):
        return render(self.request, 'account/login.html', {'login_form': form})


class LogoutView(LogoutView):

    def __init__(self, **kwargs):
        super(LogoutView, self).__init__(*kwargs)

    def logout(self):
        if Client.objects.filter(clicode=self.request.user.pk).exists():
            client = Client.objects.get(clicode=self.request.user.pk)
            type_client = TypeClient.objects.all()

            if client.tclcode == type_client.get(tclcode=3):
                managed_members = ManagerClient.objects.filter(
                    clicodemanager=client)
                for member in managed_members:
                    save_log(False, member.clicodegirl)

            save_log(False, client)

        super(LogoutView, self).logout()


class SignupView(SignupView):

    def get_context_data(self, **kwargs):
        context = super(SignupView, self).get_context_data(**kwargs)
        return context

    def form_invalid(self, form):
        return render(self.request,
                      'account/signup.html',
                      {'signup_form': form})


class Manager(ListView):
    template_name = 'dateSite/manager/login_manager.html'

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)

        girls = ManagerClient.objects.filter(
            clicodemanager=self.request.user.pk)

        list_girl = []
        i = 0
        for g in girls:
            if g.clicodegirl.cliactive is True:
                dic = g.clicodegirl.as_dict()
                c = g.clicodegirl.clicode
                dic['total'] = "%s%s" % (
                    Notification.quantityNotRead(clicode=c),
                    Message.quantityNotRead(clicode=c))
                list_girl.append(dic)
                if i <= 0:
                    i = i + 1
                    context['client'] = g.clicodegirl.client_complete()
                    # cantidad de notificaciones
                    quan = Notification.objects.filter(
                        clicoderecieved=g.clicodegirl.clicode,
                        notread=False).count()
                    context['quantity_ntf'] = quan
                    # Cantidad de inbox para la chica
                    context['quantity_inb'] = 0
                    # listado de chats y request de la primera chica
                    result = Room.getChatsRequest(g.clicodegirl.clicode)
                    if len(result) > 0:
                        if "mychats" in result:
                            context['mychats'] = result["mychats"]
                        if "myrequest" in result:
                            context['myrequest'] = result["myrequest"]

        context['girls'] = list_girl
        context['is_client'] = True
        # Sending credits cost
        context['credit_chat'] = SubService.objects.get(
            suscode=1).susquantitycredit
        context['credit_sticker'] = SubService.objects.get(
            suscode=2).susquantitycredit

        return context

    def get_queryset(self):
        return get_client_list(self.request.user)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


def about_view(request):
    return render(request, 'dateSite/about.html')

def faq_view(request):
    return render(request, 'dateSite/faq.html')


def terms_view(request):
    return render(request, 'dateSite/terms.html')


def privacy_view(request):
    return render(request, 'dateSite/policy.html')


def securely_view(request):
    return render(request, 'dateSite/securely.html')


def contact_view(request):
    return render(request, 'dateSite/contactus.html')


class Index(ListView):
    model = Client
    context_object_name = 'members'
    template_name = 'dateSite/home.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        try:
            # Obtenemos la cantidad de creditos del cliente que se conecta
            client = Client.objects.get(clicode=self.request.user.pk)
            context['credits_billing'] = Purchase.credits(client)
            context['new_inbox'] = 0
            # Obtenemos la cantidad de inbox nuevos del cliente
        except Client.DoesNotExist:
            context['credits_billing'] = 0
            context['new_inbox'] = 0

        return context

    def get_queryset(self):
        return get_client_list(self.request.user)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class AlertsView(ListView):
    model = Notification
    context_object_name = 'all_notifications'
    template_name = 'dateSite/notifications.html'

    def get_queryset(self):
        user = self.request.user
        Notification.objects.filter(
            clicoderecieved=user.pk,
            notread=False).update(
            notread=True)
        all_notifications = Notification.objects.filter(
            clicoderecieved=user.pk).order_by("-notcode")
        return all_notifications


class ProfileView(DetailView):
    model = Client
    template_name = 'dateSite/profile.html'
    slug_field = 'cliusername'
    context_object_name = 'member'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['profile_percentage'] = profile_percentage_processor(
            self.request)
        current_client = kwargs.get('object')

        album = PhotoAlbum.objects.filter(
            clicode=current_client,
            phatype=1,
            phaactive=True).order_by(
            'phacreationdate').first()

        context['album_list'] = get_client_albums(current_client)
        if album:
            context['public_album'] = Picture.objects.filter(
                picactive=True,
                phacode=album).exclude(
                picprofile=True)
            context['album_name'] = album.phaname

        context['private_collection'] = list(
            ClientCollectionAlbum.objects.filter(
                clicode=self.request.user.pk).values_list(
                'phacode', flat=True))
        context['photoalbum_form'] = UploadAlbumForm()

        try:
            sender = self.model.objects.get(pk=self.request.user.pk)
            if(current_client.clicode != sender.clicode):
                reciever = current_client
                save = True
                alert = Notification.objects.filter(
                    clicoderecieved=reciever.clicode,
                    clicodesent=sender.clicode).last()
                if alert:
                    seg = timezone.now() - alert.notdate
                    # Si no han pasado 12 horas
                    if seg.total_seconds() < 43200:
                        save = False
                if save:
                    alert = Notification(
                        notdate=datetime.now().isoformat(),
                        clicoderecieved=reciever,
                        clicodesent=sender,
                        ntycode=NotificationType.objects.get(ntycode=1)
                    )
                    alert.save()
                    if reciever.clireplychannel:
                        d = {}
                        d["notification"] = alert.as_dict()
                        d["error"] = {'type': '3'}
                        Channel(reciever.clireplychannel).send({
                            "text": json.dumps(d)
                        })
        except Client.DoesNotExist:
            d = {}
            d["notification"] = 0

        return context


class UpdateProfileView(UpdateView):
    model = Client
    form_class = EditProfileForm
    template_name = 'dateSite/edit_profile.html'
    success_url = "/"
    context_object_name = 'client'

    def form_valid(self, form):
        if self.request.method == 'POST':
            if form.is_valid():
                form_data = form.cleaned_data
                client = Client.objects.get(clicode=self.request.user.pk)
                client.cliname = form_data['cliname']
                client.clidescription = form_data['clidescription']
                client.clibirthdate = form_data['clibirthdate']
                client.inccode = form_data['inccode']
                client.gencode = form_data['gencode']
                client.citcode = form_data['citcode']
                client.marcode = form_data['marcode']
                client.educode = form_data['educode']
                client.lancodefirst = form_data['lancodefirst']
                client.lancodesecond = form_data['lancodesecond']
                client.heicode = form_data['heicode']
                client.weicode = form_data['weicode']
                client.ocucode = form_data['ocucode']
                client.ethcode = form_data['ethcode']
                client.langlevel = form_data['langlevel']
                client.bodycode = form_data['bodycode']
                client.chicode = form_data['chicode']
                client.eyecode = form_data['eyecode']
                client.haicode = form_data['haicode']
                client.hlecode = form_data['hlecode']
                client.relcode = form_data['relcode']
                client.zodcode = form_data['zodcode']
                client.frecodedrink = form_data['frecodedrink']
                client.frecodesmoke = form_data['frecodesmoke']
                client.save()
            else:
                print('error')

        return redirect('dateSite:profile', slug=self.request.user.username)

    def user_passes_test(self, request):
        if request.user.is_authenticated():
            self.object = self.get_object()
            return self.object.cliuser == request.user
        return False

    def get_object(self):
        return self.model.objects.get(pk=self.request.user.pk)

    def dispatch(self, request, *args, **kwargs):
        if not self.get_object() or not self.user_passes_test(request):
            return redirect('/')
        return super(UpdateProfileView, self).dispatch(
            self.request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UpdateProfileView, self).get_context_data(**kwargs)
        public_albums = PhotoAlbum.objects.filter(
            phaactive=True, phatype=1,
            clicode=self.request.user.pk)
        context['public_pictures'] = Picture.objects.filter(
            picactive=True, phacode__in=public_albums)
        return context


class OnlineMembers(ListView):
    model = Client
    context_object_name = 'members'
    template_name = 'dateSite/online_members.html'

    def get_context_data(self, **kwargs):
        context = super(OnlineMembers, self).get_context_data(**kwargs)
        context['signup_form'] = SignupForm()
        if self.request.user.is_anonymous:
            context['modal'] = True
        else:
            context['modal'] = False
        return context

    def get_queryset(self):
        if self.request.method == 'POST':
            min_age = self.request.POST['seaminage']
            max_age = self.request.POST['seamaxage']
            gender_preference = self.request.POST['gencode']
        else:
            min_age = 18
            max_age = 99
            gender_preference = 1
        members = get_client_list(self.request.user,
                                  min_age, max_age, None,
                                  gender_preference=gender_preference)
        return members

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
