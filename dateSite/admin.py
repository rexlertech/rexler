from django.contrib import admin
from .models.client import Client, PetClient, HobbieClient, SportClient
from .models.testimonial import Testimonial
from .models.catalog import Country, City, Gender, Marital
from .models.notification import Notification, NotificationType


@admin.register(Testimonial)
class AdminTestimonial(admin.ModelAdmin):
    list_display = ('tesname', 'tescomment', 'tespicture',
                    'tesactive', 'testype', 'tesdate')
    list_filter = ('testype',)


@admin.register(Country)
class AdminCountry(admin.ModelAdmin):
    list_display = ('couname', 'couactive')


@admin.register(City)
class AdminCity(admin.ModelAdmin):
    list_display = ('citname', 'coucode')


@admin.register(Gender)
class AdminGender(admin.ModelAdmin):
    list_display = ('genname', 'gendescription')


@admin.register(Client)
class AdminClient(admin.ModelAdmin):
    list_display = ('cliusername', 'cliemail', 'cliactive',)
    list_filter = ('gencode',)


@admin.register(Marital)
class AdminMaritalStatus(admin.ModelAdmin):
    list_display = ('marname', 'maractive',)
    list_filter = ('marcode',)


@admin.register(Notification)
class AdminNotification(admin.ModelAdmin):
    list_display = ('notdate', 'clicodesent', 'clicoderecieved',)
    list_filter = ('notdate', 'clicoderecieved')


@admin.register(NotificationType)
class AdminNotificationType(admin.ModelAdmin):
    list_display = ('ntyname', 'ntydescription', 'ntyactive',)
    list_filter = ('ntyname', 'ntyactive')


@admin.register(PetClient)
class AdminPetClient(admin.ModelAdmin):
    list_display = ('pechave', 'peclike', 'pecdontlike', 'petcode', 'clicode',)
    list_filter = ('petcode',)


@admin.register(HobbieClient)
class AdminHobbieClient(admin.ModelAdmin):
    list_display = ('hobcode', 'clicode', )
    list_filter = ('hobcode',)


@admin.register(SportClient)
class AdminSportClient(admin.ModelAdmin):
    list_display = ('clicode', 'spocode', )
    list_filter = ('spocode',)
