from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.signals import (email_confirmed, user_logged_in,
                                     user_signed_up)
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from datetime import datetime
from .models.client import Client, PhotoAlbum, Picture, ManagerClient
from .models.catalog import Gender, TypeClient, Language
from .models.log_session import LogSession
from .forms import SignupForm, GoodLuckSearchForm
from .base_helper import save_log, send_email
from django.contrib.sites.models import Site
from django.shortcuts import render, redirect
import json
import os


class AccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        if self.request.method == 'POST':
            form2 = GoodLuckSearchForm(request.POST)
            if form.is_valid() and form2.is_valid():
                user_data = form.cleaned_data
                search_data = form2.cleaned_data
                user.username = user_data['username']
                user.email = user_data['email']
                user.last_name = '{"gen":%i, "min":%i, "max":%i}' % (
                    search_data['gencode'].gencode,
                    int(search_data['seaminage']),
                    int(search_data['seamaxage']))

                if 'password1' in user_data:
                    user.set_password(user_data['password1'])
                else:
                    user.set_unusable_password()
                self.populate_username(request, user)

                if commit:
                    user.save()

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        json_gender = json.loads(
            emailconfirmation.email_address.user.last_name)
        gender_preference = Gender.objects.get(
            genpreference=json_gender['gen'])
        current_site = Site.objects.get_current()
        activate_url = self.get_email_confirmation_url(
            request,
            emailconfirmation)
        context = {
            'user': emailconfirmation.email_address.user,
            'activate_url': activate_url,
            'current_site': current_site,
            'key': emailconfirmation.key,
            'email': emailconfirmation.email_address.user.email,
            'gender_preference': gender_preference.genname,
            'image': '/static/dateSite/img/logo.png'
        }

        email_template = 'account/email/email_confirmation'
        self.send_mail(email_template,
                       emailconfirmation.email_address.email,
                       context)

    def get_login_redirect_url(self, request):
        path = "/"
        if Client.objects.filter(clicode=request.user.pk).exists():
            client = Client.objects.get(clicode=request.user.pk)
            if client.tclcode.tclcode == 3:
                path = "/manager/"

        return path

    @receiver(email_confirmed)
    def email_confirmed_(request, email_address, **kwargs):
        user = User.objects.get(email=email_address.email)
        json_gender = json.loads(user.last_name)
        client_gender = Gender.objects.get(gencode=json_gender['gen'])
        type_client = TypeClient.objects.all()

        client = Client()
        client.clicode = client.cliuser_id = user.id
        client.cliusername = user.username
        client.cliemail = user.email
        client.clipassword = user.password
        client.clidatesubscription = user.date_joined
        client.gencode = client_gender
        client.cliactive = True
        # Default
        client.lancodefirst = Language.objects.get(lanname='English')
        # TODO: Change numbers for gender and client type ENUM
        if client_gender.gencode == 1:
            client.tclcode = type_client.get(tclcode=4)
        if client_gender.gencode == 2:
            client.tclcode = type_client.get(tclcode=5)
        client.save()
        save_log(True, client)

    @receiver(user_logged_in)
    def user_logged_in_(request, user, **kwargs):
        if Client.objects.filter(clicode=user.pk).exists():
            client = Client.objects.get(clicode=user.pk)
            save_log(True, client)
            if client.tclcode.tclcode == 3:
                managed_members = ManagerClient.objects.filter(
                    clicodemanager=client.clicode)
                for member in managed_members:
                    save_log(True, member.clicodegirl)
            """
            else:
                user_logged_in.connect(user_logged_in_)
            """
