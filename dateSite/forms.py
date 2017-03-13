from django import forms
from dal import autocomplete
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.urlresolvers import reverse
from allauth.account.forms import (LoginForm, SignupForm, ResetPasswordForm,
                                   ChangePasswordForm, AddEmailForm)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Submit, Layout, Field, HTML, Div)
from crispy_forms.bootstrap import FormActions, AppendedText

from .models.clientactions import Search
from .models.client import Client, PhotoAlbum, Picture
from .models.catalog import (Gender, TypeClient, Feeling, Language, Country,
                             Ethnicity, Height, Weight, Income, Marital,
                             Occupation, Pet, Sport, Hobbie)
from django_file_form.forms import (FileFormMixin, UploadedFileField,
                                    MultipleUploadedFileField)


class LoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput()
        remember = forms.BooleanField()

        self.helper = FormHelper()
        self.helper.form_id = 'login_form'
        self.form_name = 'login_form'
        self.form_show_errors = True
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Div(
                Field('login', placeholder='EMAIL',
                      css_class='form-control input-xs',
                      error_css_class='alert alert-danger',
                      autocomplete='new-password'),
                css_class="form-group"
            ),
            Div(
                Field('password', placeholder='PASSWORD',
                      css_class='form-control input-xs',
                      error_css_class='alert alert-danger',
                      autocomplete='new-password'),
                css_class="form-group"
            ),
            FormActions(
                Submit('submit', 'Log In', css_class='btn-login')
            ),
            Div(
                AppendedText('remember', 'Remember me'),
                HTML(
                    "<div class='forgot'>"
                    "<a href={url}>{text}</a></div>".format(
                        url=reverse('account_reset_password'),
                        text=('Forgot your password?')
                    )
                ),
                css_class='form-options'
            )
        )


class SignupForm(SignupForm):

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_labels = True
        self.helper.layout = Layout(
            Field('username', css_class='input-xs',
                  placeholder='Name or username'),
            Field('email', css_class='input-xs'),
            Field('password1', css_class='input-xs'),
            Field('password2', css_class='input-xs'),
        )


class ResetPasswordForm(ResetPasswordForm):

    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('email',
                  css_class='form-control input-xs',
                  placeholder="email"),
            FormActions(
                Submit('submit', 'Reset My Password',
                       css_class='btn-signup form-control btn-xs')
            ),
        )


class ChangePasswordForm(ChangePasswordForm):

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('oldpassword', css_class='form-control',
                  placeholder="old password"),
            Field('password1', css_class='form-control',
                  placeholder="new password "),
            Field('password2', css_class='form-control',
                  placeholder="new password (again)"),
            FormActions(
                Submit('submit', 'Change My Password',
                       css_class='btn-signup form-control')
            ),
        )


class AddEmailForm(AddEmailForm):

    def __init__(self, *args, **kwargs):
        super(AddEmailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('email',
                  css_class='form-control input-xs',
                  placeholder="email"),
            FormActions(
                Submit('submit', 'Add Email',
                       css_class='btn-xs btn-primary')
            ),
        )


min_age = 18
max_age = 100
default_max_age = 30


class GoodLuckSearchForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(GoodLuckSearchForm, self).__init__(*args, **kwargs)
        self.fields['gencode'].label = "I AM A"
        self.fields['gencode'].required = True

        self.fields['seaminage'] = forms.ChoiceField(choices=(
                                                     (str(x), x)
                                                     for x in
                                                     range(min_age, max_age)))
        self.fields['seamaxage'] = forms.ChoiceField(choices=(
                                                     (str(x), x)
                                                     for x in
                                                     range(min_age, max_age)))
        self.fields['seaminage'].label = ''
        self.fields['seamaxage'].label = ''
        self.fields['seamaxage'].initial = default_max_age

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('gencode', css_class='input-xs'),
            HTML('<div class="control-group">'),
            HTML('<div class="control-label">AGES</div>'),
            HTML('<div class="controls-age">'),
            Field('seaminage', css_class='input-xs input-age',
                  placeholder='FROM'),
            Field('seamaxage', css_class='input-xs input-age',
                  placeholder='TO'),
            HTML('</div></div>'),
        )
        self.helper.form_id = 'goodluckForm'
        self.helper.form_method = 'post'

    class Meta:
        model = Search
        fields = ['gencode', 'seaminage', 'seamaxage', ]
        labels = None


class FullSearchForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        country_list = Country.objects.filter(couactive=True)
        income_list = Income.objects.all()
        maritalstatus_list = Marital.objects.filter(maractive=True)
        ethnicity_list = Ethnicity.objects.filter(ethactive=True)
        language_list = Language.objects.all()
        ocupation_list = Occupation.objects.all()
        height_list = Height.objects.all()
        weight_list = Weight.objects.all()
        pet_list = Pet.objects.filter(petactive=True)
        hobbie_list = Hobbie.objects.filter(hobactive=True)
        sport_list = Sport.objects.filter(spoactive=True)
        income_choices = ((x.inccode, str("%i — %i" % (x.incmin, x.incmax)))
                          for x in income_list)
        super(FullSearchForm, self).__init__(*args, **kwargs)
        self.fields['seaminage'] = forms.ChoiceField(
            label="",
            required=False,
            choices=((str(x), x) for x in range(min_age, max_age)))
        self.fields['seaminage'].choices.insert(0, ('', 'From'))
        self.fields['seamaxage'] = forms.ChoiceField(
            label="",
            required=False,
            choices=((str(x), x) for x in range(min_age, max_age)))
        self.fields['seamaxage'].choices.insert(0, ('', 'To'))
        self.fields['seacountry'] = forms.ChoiceField(
            label="",
            required=False,
            choices=((x.coucode, x.couname) for x in country_list))
        self.fields['seacountry'].choices.insert(0, ('', 'Country'))
        self.fields['seaincome'] = forms.ChoiceField(label="", required=False,
                                                     choices=income_choices)
        self.fields['seaincome'].choices.insert(0, ('', 'Income'))
        self.fields['seamstatus'] = forms.ChoiceField(
            label="",
            required=False,
            choices=(
                (x.marcode, x.marname) for x in maritalstatus_list))
        self.fields['seamstatus'].choices.insert(0, ('', 'Marital Status'))
        self.fields['seaethnicity'] = forms.ChoiceField(
            label="",
            required=False,
            choices=((x.ethcode, x.ethname) for x in ethnicity_list))
        self.fields['seaethnicity'].choices.insert(0, ('', 'Ethnicity'))
        self.fields['seafirstlang'] = forms.ChoiceField(
            label="",
            required=False,
            choices=((x.lancode, x.lanname) for x in language_list))
        self.fields['seafirstlang'].choices.insert(0, ('', 'First Language'))
        self.fields['seasecondlang'] = forms.ChoiceField(
            label="",
            required=False,
            choices=((x.lancode, x.lanname) for x in language_list))
        self.fields['seasecondlang'].choices.insert(0, ('', 'Second Language'))
        self.fields['seaocupation'] = forms.ChoiceField(
            label="",
            required=False,
            choices=(
                (x.ocucode, x.ocudescription) for x in ocupation_list))
        self.fields['seaocupation'].choices.insert(0, ('', 'Occupation'))
        self.fields['seaheight'] = forms.ChoiceField(
            label="",
            required=False,
            choices=(
                (x.heicode, x.heidescription) for x in height_list))
        self.fields['seaheight'].choices.insert(0, ('', 'Height'))
        self.fields['seaweight'] = forms.ChoiceField(
            label="",
            required=False,
            choices=(
                (x.weicode, x.weidescription) for x in weight_list))
        self.fields['seaweight'].choices.insert(0, ('', 'Weight'))
        self.fields['seachildren'] = forms.ChoiceField(
            label="",
            required=False,
            choices=((str(x), x) for x in range(11)))
        self.fields['seachildren'].choices.insert(0, ('', 'Children'))
        self.fields['seapet'] = forms.ChoiceField(
            label="",
            required=False,
            choices=((x.petcode, x.petname) for x in pet_list))
        self.fields['seapet'].choices.insert(0, ('', 'Pet'))
        self.fields['seasport'] = forms.ChoiceField(
            label="",
            required=False,
            choices=((x.spocode, x.sponame) for x in sport_list))
        self.fields['seasport'].choices.insert(0, ('', 'Sport'))
        self.fields['seahobbie'] = forms.ChoiceField(
            label="", required=False,
            choices=((x.hobcode, x.hobname) for x in hobbie_list))
        self.fields['seahobbie'].choices.insert(0, ('', 'Hobbie'))

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                HTML('<label class="title">Age</label>'),
                Field('seaminage', css_class='form-control-sm input-age'),
                Field('seamaxage', css_class='form-control-sm input-age'),
                HTML('<br /><label class="title">Country</label>'),
                Field('seacountry', css_class='form-control-sm'),
                css_class="simple-search"
            ),
            Div(
                css_id='search-error',
            ),
        )
        self.helper.form_id = 'searchForm'
        self.helper.form_method = 'post'

    class Meta:
        model = Search
        fields = ('seaminage', 'seamaxage', 'seacountry')
        labels = None
        widgets = {
            'seacountry': autocomplete.ModelSelect2(
                url='dateSite:country_autocomplete'
            ),
        }


class EditProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['langlevel'] = forms.ChoiceField(choices=((str(x), x)
                                                     for x in
                                                     range(1, 101)))
        self.fields['langlevel'].label = '2° Language Level'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Field('cliname', css_class='form-control'),
                Field('gencode', css_class='form-control'),
                Field('clidescription', css_class='form-control'),
                css_class='col-md-8 col-xs-12 edit-details',
            ),
            Div(
                Field('marcode', css_class='form-control'),
                Field('clibirthdate', css_class='form-control'),
                Field('citcode', css_class='form-control'),
                Field('ethcode', css_class='form-control'),
                Field('educode', css_class='form-control'),
                css_class='col-md-6 col-xs-12 column-edit',
            ),
            Div(
                Field('lancodefirst', css_class='form-control'),
                Field('lancodesecond', css_class='form-control'),
                Field('langlevel', css_class='form-control'),
                HTML('<label class="lblpercent">%</label>'),
                Field('ocucode', css_class='form-control'),
                Field('inccode', css_class='form-control'),
                css_class='col-md-6 col-xs-12 column-edit',
            ),
            Div(
                HTML('<span class="title">Physical description</span><hr >'),
                css_class='col-xs-12 separator',
            ),
            Div(
                Field('bodycode', css_class='form-control'),
                Field('heicode', css_class='form-control'),
                Field('weicode', css_class='form-control'),
                css_class='col-md-6 col-xs-12 column-edit',
            ),
            Div(
                Field('eyecode', css_class='form-control'),
                Field('haicode', css_class='form-control'),
                Field('hlecode', css_class='form-control'),
                css_class='col-md-6 col-xs-12 column-edit',
            ),
            Div(
                HTML('<span class="title">Other</span><hr >'),
                css_class='col-xs-12 separator',
            ),
            Div(
                Field('frecodedrink', css_class='form-control'),
                Field('frecodesmoke', css_class='form-control'),
                Field('zodcode', css_class='form-control'),
                css_class='col-md-6 col-xs-12 column-edit',
            ),
            Div(
                Field('relcode', css_class='form-control'),
                Field('chicode', css_class='form-control'),
                css_class='col-md-6 col-xs-12 column-edit',
            ),
            FormActions(
                Submit('submit', 'SAVE', css_class='btn-primary form-control')
            ),
        )

    class Meta:
        model = Client
        fields = ('cliname', 'clidescription', 'clibirthdate', 'langlevel',
                  'inccode', 'gencode', 'citcode', 'marcode', 'educode',
                  'lancodefirst', 'lancodesecond', 'heicode', 'weicode',
                  'ocucode', 'ethcode', 'eyecode', 'haicode', 'hlecode',
                  'frecodedrink', 'frecodesmoke', 'zodcode', 'relcode',
                  'chicode', 'bodycode')
        labels = {
            'cliname': 'Name',
            'clidescription': 'About me',
            'clibirthdate': 'Birthdate',
            'inccode': 'Anual Income',
            'gencode': 'Gender',
            'citcode': 'City',
            'marcode': 'Marital Status',
            'educode': 'Education Level',
            'lancodefirst': '1° Language',
            'lancodesecond': '2° Language',
            'heicode': 'Height',
            'weicode': 'Weight',
            'ocucode': 'Occupation',
            'ethcode': 'Ethnicity',
            'eyecode': 'Eyes color',
            'haicode': 'Hair color',
            'hlecode': 'Hair Length',
            'frecodedrink': 'Drinking',
            'frecodesmoke': 'Smoking',
            'zodcode': 'Zodiac',
            'relcode': 'Belief',
            'chicode': 'Kids',
            'bodycode': 'Body type',
        }

        widgets = {
            'ocucode': autocomplete.ModelSelect2(
                url='dateSite:occupation_autocomplete'
            ),
            'clidescription': forms.Textarea(attrs={'rows': 5, 'cols': 15}),
            'clibirthdate': forms.DateInput(attrs={'class': 'datepicker'}),
        }


class UploadAlbumForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UploadAlbumForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Field('phaname', css_class='form-control album-name'),
                Field('phatype', css_class='form-control album-type'),
            ),
            Field('phadescription', css_class='form-control'),
        )

    class Meta:
        model = PhotoAlbum
        fields = ['phaname', 'phatype', 'phadescription', ]
        labels = {
            'phaname': 'Album Name',
            'phadescription': 'About this album',
            'phatype': 'This album is',
        }
        widgets = {
            'phadescription': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
        }


class UploadFilesForm(FileFormMixin, forms.Form):
    input_files = MultipleUploadedFileField()
