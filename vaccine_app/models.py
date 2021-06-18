from django.db import models
from datetime import datetime,date    
import os,pytz
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
import uuid
# Create your models here.

#wherever you want to add user add the keyword 'settings.AUTH_USER_MODEL'

lot_status = ( 
    ("produced","produced"), 
    ("transitToDistrict","transitToDistrict"), 
    ("atDistrict","atDistrict"), 
    ("transitToCenter","transitToCenter"), 
    ("atCenter","atCenter"), 
    ("consumed","consumed"), 
) 


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, email, first_name, last_name, aadharNumber, password, **other_fields):
        other_fields.setdefault('is_superuser', True)

        other_fields.setdefault('is_districtadmin', True)
        other_fields.setdefault('is_centeradmin', True)
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')

        if other_fields.get('is_districtadmin') is not True:
            raise ValueError(
                'Superuser must be assigned to is_districtadmin=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')
        if other_fields.get('is_centeradmin') is not True:
            raise ValueError(
                'Superuser must be assigned to is_centeradmin=True.')

        return self.create_user(email,first_name,last_name,aadharNumber,password,**other_fields)

    def create_user(self, email, first_name, last_name, aadharNumber, password, **other_fields):
        if not email:
            raise ValueError('Provide email')
        email=self.normalize_email(email)
        user=self.model(email=email, first_name=first_name, last_name=last_name, aadharNumber=aadharNumber, **other_fields)
        user.set_password(password)
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email=models.EmailField(unique=True)
    first_name=models.CharField(max_length=150)
    last_name=models.CharField(max_length=150)
    aadharNumber=models.CharField(max_length=30, unique=True, )
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['first_name','last_name','aadharNumber']

    is_active=models.BooleanField(default=False)
    
    is_superuser=models.BooleanField(default=False)
    is_districtadmin=models.BooleanField(default=False)
    is_centeradmin=models.BooleanField(default=False)

    is_staff=models.BooleanField(default=False)
    objects=CustomAccountManager()
    def __str__(self):
        return self.email


class VaccineLot(models.Model):
    lotId = models.AutoField(primary_key=True)
    status=models.CharField(max_length = 20, choices = lot_status, default = 'produced')
    productionTimestamp = models.DateTimeField(auto_now_add=True)
    departureTimestamp = models.DateTimeField(blank = True, null=True, default=None)
    countOfDosesConsumed = models.IntegerField(default = 0)
    def __str__(self):
        return str(self.lotId) + self.status


class District(models.Model):
    districtPrimaryKey = models.AutoField(primary_key=True)
    districtId = models.UUIDField(default=uuid.uuid4, unique=True)   
    # userName = models.CharField(max_length=255)
    name = models.CharField(max_length=255, unique=True)
    population = models.IntegerField(default=1)
    # password = models.CharField(max_length=20)
    def __str__(self):
        return self.name

class DistrictVaccineData(models.Model):
    district = models.ForeignKey(District,on_delete=models.CASCADE,related_name="districtVaccine")
    lot = models.OneToOneField(VaccineLot, on_delete=models.CASCADE,related_name="districtVaccine")
    arrivalTimestamp = models.DateTimeField(blank = True, null=True, default=None)
    departureTimestamp = models.DateTimeField(blank = True, null=True, default=None)
    def __str__(self):
        return self.district.name + str(self.lot.lotId) + self.lot.status

#TODO check districtvaccinedata table if it's working
#TODO lot should be 1-1 because 1 entry corresponding to one lot


class Center(models.Model):
    centerPrimaryKey = models.AutoField(primary_key=True)
    centerId = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="Center")
    # userName = models.CharField(max_length=255)
    name = models.CharField(max_length=255, unique=True)
    maxCountPerDate = models.IntegerField(default=10)
    population = models.IntegerField(default=1)
    # password = models.CharField(max_length=20)
    def __str__(self):
        return self.name

class CenterVaccineData(models.Model):
    center = models.ForeignKey(Center, on_delete=models.CASCADE, related_name="centerVaccine")
    lot = models.OneToOneField(VaccineLot, on_delete=models.CASCADE, related_name="centerVaccine")
    arrivalTimestamp = models.DateTimeField(blank = True, null=True, default=None)
    def __str__(self):
        return self.center.name + str(self.lot.lotId) + self.lot.status

#TODO check CenterVaccineData table if it's working, make lot one to one field to 

class CenterRegestration(models.Model):
    center = models.ForeignKey(Center,on_delete=models.CASCADE,related_name="centerRegestrations")
    date = models.DateField(blank = False, null=False)
    count = models.IntegerField()
    class Meta:
        unique_together = (("center", "date"),)


class Receiver(models.Model):
    aadharNumber = models.CharField(max_length=16, unique=True, primary_key=True) 
    center = models.ForeignKey(Center,on_delete=models.CASCADE,related_name="receiver")
    name = models.CharField(max_length=255)
    contactNumber= models.CharField(max_length=12, )
    address = models.CharField(max_length=1000, null = True)
    appointmentDate = models.DateField(blank = True, null=True, default=None)
    def __str__(self):
        return self.center.name + "_" + str(self.appointmentDate)

class ReceiverVaccination(models.Model):
    receiver = models.OneToOneField(Receiver, on_delete=models.CASCADE,related_name="receiverVaccination")
    lot = models.ForeignKey(VaccineLot, on_delete=models.CASCADE,related_name="receiverVaccination")
    vaccineDose = models.BooleanField(default = True)


class AccessControlListDistrict(models.Model):
    person=models.ForeignKey(User,on_delete=models.CASCADE,related_name="access_control_list_district_person")
    district=models.ForeignKey(District,on_delete=models.CASCADE,related_name="access_control_list_district")
    class Meta:
        unique_together = (("person", "district"),)


class AccessControlListCenter(models.Model):
    person=models.ForeignKey(User,on_delete=models.CASCADE,related_name="access_control_list_center_person")
    center=models.ForeignKey(Center,on_delete=models.CASCADE,related_name="access_control_list_center")
    class Meta:
        unique_together = (("person", "center"),)


class Keys(models.Model):
    person=models.EmailField()
    key=models.UUIDField(editable=False, unique=True)
    district_name=models.CharField(max_length=255)
    center_name=models.CharField(max_length=255)
    class Meta:
        unique_together = (("person", "key"),)


#TODO if a user is a distreict or center admin they should access their own center or admin
#TODO Create Authentication table fields user and the access tokens or primary key of centers. Create logging of every user


#TODO 

#  vashi 1hheheh