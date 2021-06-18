from django.urls import path
from . import views,urls
from django.conf import settings



urlpatterns = [
    path('', views.index,name="index"),
    path('send_to_district',views.send_to_district,name='send_to_district'),
    path('register', views.register_user,name="register"),
    path('registerForVaccinationDistrictForm', views.registerForVaccinationDistrictForm,name="registerForVaccinationDistrictForm"),
    path('registerForVaccination/<str:district_name>/<str:center_name>', views.registerForVaccination,name="registerForVaccination"),
    # path('centeradd_upload',views.centeradd_upload,name='centeradd_upload'),
    # path('loggedin/<district_or_center>/<name>/',views.loggedin,name='loggedin'),
    path('login',views.login_gen,name='login_gen'),
    path('logout',views.logout,name='logout'),
    path('provideaccess',views.provideaccess,name='provideaccess'),
    path('currentStatus',views.currentStatus,name='currentStatus'),

    path('dashboard/district/<name>/',views.district_dash,name='district_dash'),
    path('district/<str:name>/updateArrivalTimeDistrict/<int:lotId>/',views.updateArrivalTimeDistrict,name='updateArrivalTimeDistrict'),
    path('district/<str:name>/send_to_center',views.send_to_center,name="send_to_center"),

    path('dashboard/center/<name>/',views.center_dash,name='center_dash'),
    path('center/<str:name>/updateMaxCountPerDate/',views.updateMaxCountPerDate,name='updateMaxCountPerDate'),
    path('center/<str:name>/updateArrivalTimeCenter/<int:lotId>/',views.updateArrivalTimeCenter,name='updateArrivalTimeCenter'),
    path('center/<str:name>/receiverVaccination/',views.receiverVaccination,name='receiverVaccination'),


    path('dashboard/',views.dashboard,name='dashboard'),

    path('give_access_megaCenter', views.give_access_megaCenter, name='give_access_megaCenter')
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns +=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)