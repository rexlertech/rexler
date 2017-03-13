from django import forms
from django.db.models import Q, Max, Count
from allauth.account.models import EmailAddress
from .base_helper import get_current_client
from .forms import (LoginForm, FullSearchForm, GoodLuckSearchForm, SignupForm,
                    ChangePasswordForm, UploadFilesForm)
from .models.client import Client
from .models.catalog import Feeling
from .models.notification import Notification
from .models.service import SubService
from .models.chat import Room, Message
from .models.purchase import Purchase


def signup_form_processor(request):
    context = {
        'signup_form': SignupForm()
    }
    return context


def login_form_processor(request):
    context = {
        'login_form': LoginForm()
    }
    return context


def goodluck_form_processor(request):
    context = {
        'goodluck_form': GoodLuckSearchForm()
    }
    return context


def changepass_form_processor(request):
    context = {
        'changepass_form': ChangePasswordForm()
    }
    return context


def user_verified_processor(request):
    context = {
        'verified': False
    }
    if not request.user.is_anonymous():
        if EmailAddress.objects.filter(
                user=request.user,
                verified=True).exists():
            context['verified'] = True

    return context


def search_form_processor(request):
    context = {
        'search_form': FullSearchForm()
    }
    return context


def feeling_choices_processor(request):
    context = {
        'feeling_choices': Feeling.objects.filter(feeactive=True),
        'feel': '/static/dateSite/img/icons/heart-icon.png',
    }

    if Client.objects.filter(clicode=request.user.pk).exists():
        client = Client.objects.get(clicode=request.user.pk)
        if client.feecode:
            context['feel'] = client.feecode.feeiconfile.url

    return context


def profile_menu_processor(request):
    context = {}
    if Client.objects.filter(clicode=request.user.pk).exists():
        current_client = Client.objects.get(clicode=request.user.pk)
        context['client'] = current_client
        context['username'] = current_client.cliusername
        context['name'] = current_client.cliname
        context['city'] = current_client.citcode
        context['marital_status'] = current_client.marcode
        context['height'] = current_client.heicode
        context['profile_picture'] = current_client.profile_picture
        context['profile_percentage'] = profile_percentage_processor(request)

    return context


def notifications_processor(request):
    notifications = Notification.objects.filter(
        clicoderecieved=get_current_client(request),
        notread=False).order_by('-notcode')
    quan = len(notifications)
    context = {
        'notifications': notifications[:5],
        'quantity_ntf': quan
    }
    return context


def profile_percentage_processor(request):
    percentage = 0
    if Client.objects.filter(clicode=request.user.pk).exists():
        client = Client.objects.get(clicode=request.user.pk)
        if client.cliname:
            percentage += 1
        if client.clidescription:
            percentage += 1
        if client.clibirthdate:
            percentage += 1
        if client.cliemail:
            percentage += 1
        if client.inccode:
            percentage += 1
        if client.gencode:
            percentage += 1
        if client.citcode:
            percentage += 1
        if client.marcode:
            percentage += 1
        if client.educode:
            percentage += 1
        if client.lancodefirst:
            percentage += 1
        if client.lancodesecond:
            percentage += 1
        if client.heicode:
            percentage += 1
        if client.weicode:
            percentage += 1
        if client.ocucode:
            percentage += 1
        if client.ethcode:
            percentage += 1

        return int(percentage * 100) / 15
    return percentage


def my_chats_processor(request):
    context = {}
    context['is_client'] = True

    result = Room.getChatsRequest(request.user.pk)

    if len(result) > 0:
        if "mychats" in result:
            context['mychats'] = result["mychats"]
        if "myrequest" in result:
            context['myrequest'] = result["myrequest"]

    # Sending credits cost
    context['credit_chat'] = SubService.objects.get(
        suscode=1).susquantitycredit
    context['credit_sticker'] = SubService.objects.get(
        suscode=2).susquantitycredit

    return context


def billing_processor(request):
    context = {
        'credits': 0
    }
    if not request.user.is_anonymous():
        if Client.objects.filter(clicode=request.user.pk).exists():
            client = Client.objects.get(clicode=request.user.pk)
            context = {
                'clisender': client.as_dict(),
                'credits': Purchase.credits(client)
            }

    return context


def upload_files_processor(request):
    context = {
        'upload_files_form': UploadFilesForm()
    }
    return context
