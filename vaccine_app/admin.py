from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import VaccineLot, District, DistrictVaccineData, Center, CenterVaccineData, CenterRegestration, Receiver, ReceiverVaccination, AccessControlListCenter,AccessControlListDistrict
# Register your models here.
from .models import User

admin.site.register(District)
admin.site.register(DistrictVaccineData)
admin.site.register(Center)
admin.site.register(CenterVaccineData)
admin.site.register(CenterRegestration)
admin.site.register(Receiver)
admin.site.register(ReceiverVaccination)
admin.site.register(AccessControlListCenter)
admin.site.register(AccessControlListDistrict)




class UserAdminConfig(UserAdmin):
  search_fields=('email','first_name','aadharNumber')
  list_filter=('email', 'is_superuser','is_districtadmin','is_centeradmin')
  ordering=('is_superuser','email')
  list_display=('email','first_name','is_superuser','is_districtadmin','is_centeradmin')
  fieldsets = (
        (None, {'fields': ('email', 'first_name','last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active','is_superuser','is_districtadmin','is_centeradmin')}),
        ('Personal', {'fields': ('aadharNumber',)}),
    )
  add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name','last_name','aadharNumber', 'password1', 'password2','is_staff', 'is_active','is_superuser','is_districtadmin','is_centeradmin')}
         ),
    )


class VaccineLotConfig(admin.ModelAdmin):
  search_fields=('lotId','status')
  list_filter=('status', 'productionTimestamp','departureTimestamp')
  ordering=('lotId',)
  list_display=('lotId','status','productionTimestamp','departureTimestamp','countOfDosesConsumed')
  fieldsets = (
        ('Edit Values', {'fields': ('status','departureTimestamp','countOfDosesConsumed')}),
    )
  add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ( 'status','productionTimestamp','departureTimestamp', 'countOfDosesConsumed')}
         ),
    )

admin.site.register(User, UserAdminConfig)
admin.site.register(VaccineLot, VaccineLotConfig)
