from django.shortcuts import render,redirect
from django.http import HttpResponse
# from django.contrib.auth.models import  User,auth
from .models import VaccineLot, District, DistrictVaccineData, Center, CenterVaccineData, CenterRegestration, Receiver, ReceiverVaccination, AccessControlListCenter,AccessControlListDistrict, Keys
from datetime import datetime
from .models import User
from .forms import RegistrationForm, ProvideAccessForm
from django.contrib.auth import authenticate, login, logout, models
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import uuid
import datetime
import sys
from math import floor,ceil
# import logging
from smtplib import SMTPException
from django.conf import settings 
from django.core.mail import send_mail 

@login_required(login_url="admin:login")
def give_access_megaCenter(request):
    error=[]
    if request.method == "POST":

        email=request.POST.get('email')
        center_name=request.POST.get('center_name')
        district_name=request.POST.get('district_name')

        if district_name != "_":
            if District.objects.filter(name=district_name).exists():
                if not Keys.objects.filter(person=email, district_name=district_name).exists():
                    district_obj=District.objects.get(name=district_name)
                    key=district_obj.districtId

                    district_obj.districtId=uuid.uuid4()
                    district_obj.save()


                    Keys.objects.create(person=email,district_name=district_name,key=key)

                    recipient_list = [email, ] 
                    subject = 'Access to '+str(email)+' for '+str(district_name)
                    message = str(district_name) + ' key = '+ str(key.urn[9:])
                    email_from = settings.EMAIL_HOST_USER 
                    
                    try:
                        send_mail( subject, message, email_from, recipient_list )
                    except SMTPException as e:
                        print('There was an error sending an email: ', e) 
                    return redirect('/admin')
                else:
                    error.append("Already given access")
            else:
                error.append("No district exists")


        if center_name != "_":
            if Center.objects.filter(name=center_name).exists():
                if not Keys.objects.filter(person=email,center_name=center_name).exists():

                    center_obj=Center.objects.get(name=center_name)
                    key=center_obj.centerId

                    center_obj.centerId=uuid.uuid4()
                    center_obj.save()

                    Keys.objects.create(person=email,center_name=center_name,key=key)

                    recipient_list = [email, ] 
                    subject = 'Access to '+str(email)+' for '+str(center_name)
                    message = str(center_name) + ' key = '+ str(key.urn[9:])
                    email_from = settings.EMAIL_HOST_USER 
                    
                    try:
                        send_mail( subject, message, email_from, recipient_list )
                    except SMTPException as e:
                        print('There was an error sending an email: ', e)
                    return redirect('/admin') 
                else:
                    error.append("Already given access")

            else:
                error.append("Invalid center name")
    return render(request, "admin/giveaccessmegacenter.html", {"error": error})

# logging.basicConfig(filename="std.log", 
# 					format='%(asctime)s %(message)s', 
# 					filemode='w') 
# logger=logging.getLogger() 
# logger.setLevel(logging.DEBUG) 
# Create your views here.
def index(request):
    # objs = [VaccineLot() for i in range(40)]
    # VaccineLot.objects.bulk_create(objs,batch_size=40)
    lots = VaccineLot.objects.all()
    total_consumed = 0
    # str1=str(total_consumed)+"Registered"
    # logger.info(str1)
    for lot in lots:
        total_consumed += lot.countOfDosesConsumed
    return render(request,"index.html", {"total_doses_consumed":total_consumed})


def register_user(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            email=registerForm.cleaned_data["email"]
            # user = registerForm.save(commit=False)
            center_name=registerForm.cleaned_data["center_name"]
            district_name=registerForm.cleaned_data["district_name"]
            key=registerForm.cleaned_data["key"]
            if center_name != "_":
                center_obj=Center.objects.get(name=center_name)
                key_obj=Keys.objects.filter(person=email,center_name=center_name)
                if key_obj.exists():

                    if key==key_obj[0].key.urn[9:]:
                        user=User.objects.create(email=email)
                        user.aadharNumber=registerForm.cleaned_data["aadharNumber"]
                        user.first_name=registerForm.cleaned_data["first_name"]
                        user.last_name=registerForm.cleaned_data["last_name"]
                        user.set_password(registerForm.cleaned_data["password"])
                        user.is_active = True
                        AccessControlListCenter.objects.create(
                            person=user,
                            center=center_obj
                        )
                        user.is_centeradmin=True
                        user.save()
                        # center_obj.centerId=uuid.uuid4()
                        # center_obj.save()
                        return redirect('dashboard')

            if district_name != "_":
                district_obj=District.objects.get(name=district_name)
                key_obj=Keys.objects.filter(person=email,district_name=district_name)
                if key_obj.exists():
                    if key==key_obj[0].key.urn[9:]:
                        user=User.objects.create(email=registerForm.cleaned_data["email"])
                        user.aadharNumber=registerForm.cleaned_data["aadharNumber"]
                        user.first_name=registerForm.cleaned_data["first_name"]
                        user.last_name=registerForm.cleaned_data["last_name"]
                        user.set_password(registerForm.cleaned_data["password"])
                        user.is_active = True
                        AccessControlListDistrict.objects.create(
                            person=user,
                            district=district_obj
                        )
                        user.is_centeradmin=True
                        user.is_districtadmin=True
                        user.save()
                        # district_obj.districtId=uuid.uuid4()
                        # district_obj.save()
                        # str1=str(user.aadharNumber)+" Registered"
                        # logger.info(str1)   
                        return redirect('dashboard')
            # user.save()

    else:
        registerForm = RegistrationForm()
    return render(request, "register.html", {"form": registerForm})


def logout(request):
    models.auth.logout(request)
    return redirect('/')
# def register_admin(request):
#     if request.user.is_authenticated:
#         return redirect('provide_access')

#     if request.method == "POST":
#         registerForm = RegistrationForm(request.POST)
#         print("INside post")
#         if registerForm.is_valid():
#             print("Inside form")
#             # user = registerForm.save(commit=False)
#             user=User.objects.create(email=registerForm.cleaned_data["email"])
#             user.aadharNumber=registerForm.cleaned_data["aadharNumber"]
#             user.first_name=registerForm.cleaned_data["first_name"]
#             user.last_name=registerForm.cleaned_data["last_name"]
#             user.set_password(registerForm.cleaned_data["password"])
#             user.is_active = True
#             user.save()
#             return redirect('provide_access')
#     else:
#         registerForm = RegistrationForm()
#     return render(request, "register.html", {"form": registerForm})

# def provide_access(request):
#     if request.user.is_authenticated:
        
#         return redirect('provide_access')
#     else:
#         return redirect('register_admin')
# def login_gen(request):
#     if request.user.is_authenticated:
#         return redirect('loggedin')
#     err=""
#     if request.method == 'POST':
#         username = request.POST.get('email')
#         password = request.POST.get('password')
#         user = authenticate(request, email = username, password = password)
#         if user is not None:
#             models.auth.login(request, user)
#             return redirect('loggedin')
#         else:
#            err = 'Input correct email and password'
#     template_name = 'login.html'
#     context={'err':err}
#     return render(request, template_name,context)



def login_gen(request):
    template_name = 'login.html'
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect('dashboard')
        # if request.user.is_districtadmin:
        #     access_obj=AccessControlListDistrict.objects.get(person=request.user)
        #     redirect('/loggedin_district/district/'+access_obj.districtID.name)
        # elif request.user.is_centeradmin:
        #     access_obj=AccessControlListCenter.objects.get(person=request.user)
        #     redirect('/loggedin/center/'+access_obj.centerID.name)
        # else :
    error=[]
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        # center = request.POST.get('center')
        # district = request.POST.get('district')
        user = authenticate(request, email = username, password = password)
        
        #TODO add_drop_down and center selection
        # if center!="_" and district!="_":
        #     error.append("You can only login to one location, either district or center.")
        #     context={'error':error}
        #     return render(request, template_name,context)
        if user is not None:
            models.auth.login(request,user)
            return redirect('dashboard')
        else:
            error.append("Invalid User")

        # if user is not None:
        #     if center and center!="_":
        #         center_obj=Center.objects.filter(name=center)
        #         if center_obj.exists():
        #             center_obj=center_obj[0]
        #             if AccessControlListCenter.objects.filter(person=user,center=center_obj).exists() and user.is_centeradmin:
        #                 models.auth.login(request, user)
        #                 return redirect('/loggedin/center/'+center_obj.name)

        #             elif AccessControlListDistrict.objects.filter(person=user,district=center_obj.district).exists() and user.is_districtadmin:
        #                 models.auth.login(request, user)
        #                 return redirect('/loggedin/center/'+center_obj.name)
        #             else:
        #                 error.append("You don't have access to"+center_obj.name)
        #         else:
        #             error.append("Center Does not Exist")
        #         # center_obj=Center.objects.get(name=center)

        #     if district and district!="_":
        #         district_obj=District.objects.filter(name=district)
        #         if district_obj.exists():
        #             district_obj=district_obj[0]
        #             if AccessControlListDistrict.objects.filter(person=user,district=district_obj).exists() and user.is_districtadmin:
        #                 models.auth.login(request, user)
        #                 return redirect('/loggedin_district/district/'+district_obj.name)
        #             else:
        #                 error.append("You don't have access to"+district_obj.name)
        #         else:
        #             error.append("District does not exist")
                
        # else:
        #     error.append("invalid user")
    
    
    context={'error':error}
    return render(request, template_name,context)

@login_required(login_url="login_gen")
def dashboard(request):
    user=request.user
    # str1=str(user.aadharNumber)+" Logged In"
    # logger.info(str1)   
    # solve login
    # or remove
    center_access=AccessControlListCenter.objects.filter(person=user)
    # If user has access to only one center
    if not user.is_districtadmin and center_access.count()==1:
        # center_access=center_access[0]
        return redirect('/dashboard/center/'+center_access[0].center.name)


    if user.is_districtadmin:
        district_access=AccessControlListDistrict.objects.filter(person=user)
        center_name=[]
        district_name=[]
        for district in district_access:
            district_name.append(district.district.name)
            center_objs=Center.objects.filter(district=district.district)
            for center in center_objs:
                center_name.append(center.name)
        if center_access.count()!=0:
            for center in center_access:
                center_name.append(center.center.name)
        return render(request,'dashboard.html',{'centers':center_name,'districts':district_name})


        # redirect('/loggedin_district/district/'+access_obj.districtID.name)
    elif request.user.is_centeradmin and not user.is_districtadmin:
        center_name=[]
        district_name=[]
        for center in center_access:
            center_name.append(center.center.name)
        return render(request,'dashboard.html',{'centers':center_name,'districts':district_name})
    else :
        return redirect('login_gen')
    


# def loggedin(request,district_or_center,name):
#     # return HttpResponse("user is"+district_or_center+name)
#     if district_or_center=="district":
#         user=request.user
#         if District.objects.filter(name=name).exists():
#             district_obj=District.objects.get(name=name)
#             if AccessControlListDistrict.objects.filter(person=user,district=district_obj).exists() and user.is_districtadmin:
#                 return redirect('dashboard/district/'+district_obj.name)
#                 #TODO Make District Dashboard
#             else:
#                 return render(request,"fail.html")
#         else:
#             return render(request,"fail.html")
#     elif district_or_center=="center":
#         user=request.user
#         if Center.objects.filter(name=name).exists():
#             center_obj=Center.objects.get(name=name)
#             if AccessControlListCenter.objects.filter(person=user,center=center_obj).exists() and user.is_centeradmin:
#                 return HttpResponse("user is"+request.user.first_name+" Center "+name)
#             elif AccessControlListDistrict.objects.filter(person=user,district=center_obj.district).exists() and user.is_districtadmin:           
#                 return HttpResponse("user is"+request.user.first_name+" center "+center_obj.name)
#             else:
#                 return render(request,"fail.html")
#         else:
#             return render(request,"fail.html")
#     else:
#         return render(request,"fail.html")

@login_required(login_url="login_gen")
def provideaccess(request):
    if request.method == "POST":
        provide_access_form = ProvideAccessForm(request.user,request.POST)
        if provide_access_form.is_valid():
            # user = registerForm.save(commit=False)
            email=request.user.email
            center_name=provide_access_form.cleaned_data["center_name"]
            district_name=provide_access_form.cleaned_data["district_name"]
            key=provide_access_form.cleaned_data["key"]
            if center_name != "_":
                key_obj=Keys.objects.filter(person=email,center_name=center_name)
                if key_obj.exists():
                    center_obj=Center.objects.get(name=center_name)
                    if key==key_obj[0].key.urn[9:]:      
                        user=User.objects.get(email=request.user.email)
                        AccessControlListCenter.objects.create(
                            person=user,
                            center=center_obj
                        )
                        user.is_centeradmin=True
                        user.save()
                        # center_obj.centerId=uuid.uuid4()
                        # center_obj.save()
                        return redirect('dashboard')
                
            if district_name != "_":
                key_obj=Keys.objects.filter(person=email,district_name=district_name)
                if key_obj.exists():
                    district_obj=District.objects.get(name=district_name)
                    if key==key_obj[0].key.urn[9:]:
                        user=User.objects.get(email=request.user.email)
                        AccessControlListDistrict.objects.create(
                            person=user,
                            district=district_obj
                        )
                        user.is_centeradmin=True
                        user.is_districtadmin=True
                        user.save()
                        # district_obj.districtId=uuid.uuid4()
                        # district_obj.save()
                        return redirect('dashboard')
            # user.save()

    else:
        provide_access_form = ProvideAccessForm(request.user)
    return render(request, "provideaccess.html", {"form": provide_access_form})

def verify(request,district_or_center,name):
    if district_or_center=="district":
        user=request.user
        if District.objects.filter(name=name).exists():
            district_obj=District.objects.get(name=name)
            if AccessControlListDistrict.objects.filter(person=user,district=district_obj).exists() and user.is_districtadmin:
                return True
            else:
                print("access is not there for user "+user.email)
                return False
        else:
            print("District name is invalid")
            return False
    elif district_or_center=="center":
        user=request.user
        if Center.objects.filter(name=name).exists():
            center_obj=Center.objects.get(name=name)
            if AccessControlListCenter.objects.filter(person=user,center=center_obj).exists() and user.is_centeradmin:
                return True
            elif AccessControlListDistrict.objects.filter(person=user,district=center_obj.district).exists() and user.is_districtadmin:
                return True
            else:
                print("access not present "+user.email)
                return False
        else:
            print("center name does not exist")
            return False
    else:
        print("Invalid district_or_center value")
        return False



@login_required
def district_dash(request,name):
    if name=="":
        return redirect('dashboard')
    if verify(request,"district",name):
        district_obj=District.objects.get(name=name)
        #dist = AccessControlListDistrict.objects.get(person = request.user,district=district_obj[0])
        #dist_ID = dist.district
        centers = Center.objects.filter(district=district_obj)
        vaccine_lots = DistrictVaccineData.objects.filter(district = district_obj)
        error=[]
        if request.method=="POST":
            nameOfCenter = request.POST['name']
            population = request.POST['population']
            if Center.objects.filter(name=nameOfCenter).exists():
                error.append("Center Already Exists")
            else:
                new_center=Center(name=nameOfCenter,district=district_obj,population=population)
                new_center.save()
            
        return render(request,'district_dash.html',{'centers':centers, 'error':error, 'vaccine_lots':vaccine_lots,'name':name})
    else:
        return redirect('dashboard')


def get_ratio_district():
    count_of_vaccine_in_produced_state=VaccineLot.objects.filter(status="produced").count()
    district_obj=District.objects.all()
    ratio_dict={}
    if(count_of_vaccine_in_produced_state==0):
        
        for district in district_obj.iterator():
            ratio_dict[district.name]=int(0)
        return ratio_dict
    population_dict={}
    min_value=sys.maxsize
    max_value=0
    for district in district_obj.iterator():
        population_dict[district.name]=int(district.population)
        if(district.population < min_value):
            min_value=district.population
        if(district.population > max_value):
            max_value=district.population
    population_ratio_dict={}
    sum_of_ratio=0
    if(min_value==0):
        min_value=1

    for district in district_obj.iterator():
        population_ratio_dict[district.name]=ceil(district.population/min_value)
        sum_of_ratio+=population_ratio_dict[district.name]
    # if(sum_of_ratio > count_of_vaccine_in_produced_state):
    #     while(sum_of_ratio > count_of_vaccine_in_produced_state):
    #         quantity_subtract=count_of_vaccine_in_produced_state-sum_of_ratio
    #         sum_of_ratio=0
    #         count=0
    #         for key in population_ratio_dict:

    #             print(int(population_ratio_dict[key])>0,quantity_subtract<0,quantity_subtract,count<quantity_subtract)

    #             if(int(population_ratio_dict[key])>0 and count<abs(quantity_subtract)):
    #                 population_ratio_dict[key]-=1
    #                 count+=1
    #                 print(key)
    #                 print(population_ratio_dict)
    #             sum_of_ratio+=population_ratio_dict[key]
                # quantity_subtract=count_of_vaccine_in_produced_state-sum_of_ratio
    ratio_multiplication_factor = count_of_vaccine_in_produced_state / sum_of_ratio
    for district in district_obj:
        ratio_dict[district.name] = floor(ratio_multiplication_factor * population_ratio_dict[district.name])

    return ratio_dict


    # if count is less than district count and if count is less than total sum of ratios
    


    

@login_required(login_url="admin:login")
def send_to_district(request):
    if request.user.is_superuser:
        #if request.method == "POST":
        error = ""
        districts = District.objects.all() 
        if request.method == "POST":
            district_names = request.POST.getlist('districts')
            lot_quantities = request.POST.getlist('quantities')
            district_quantities = list(zip(district_names,lot_quantities))
            error = ""
            count = 0
            for district_name,lot_quantity in district_quantities:
                if(int(lot_quantity) > 0):
                    count = int(lot_quantity)
                    while count != 0:
                        lots_count = VaccineLot.objects.filter(status = "produced").count()
                        if(lots_count > 0):
                            lot =  VaccineLot.objects.filter(status = "produced")[0]
                            district = District.objects.get(name = district_name)
                            district_vaccine_obj = DistrictVaccineData.objects.create(lot = lot, district=district)
                            district_vaccine_obj.save()
                            lot.status = "transitToDistrict"
                            lot.departureTimestamp = datetime.datetime.now()
                            lot.save()
                            count -= 1
                            # str1=str(request.user.aadharNumber)+" sent to"
                            # logger.info(str1)   
                        else:
                            error = "Quantities were assigned upto district: " + district_name 
                            break
        
        # Get recommended count
        ratio=get_ratio_district()
        ratio_list=[]
        count_list=[]
        for district in districts:
            count_list.append(DistrictVaccineData.objects.filter(district=district, lot__status__contains = "atDistrict").count())
            ratio_list.append(ratio[district.name])

        
        
        quantity_available = VaccineLot.objects.filter(status = "produced").count()
        context = {"districts":zip(districts,zip(ratio_list,count_list)),"quantity_available":quantity_available,"error":error, "ratio":ratio}
        return render(request,"admin/send_to_district.html",context)
    return redirect("admin")


def updateArrivalTimeDistrict(request, name, lotId):
    if verify(request,"district",name):
        district_vaccine_obj = DistrictVaccineData.objects.filter(lot__lotId__contains = lotId, district__name__contains = name)
        if(district_vaccine_obj.exists()):
            district_vaccine_obj = DistrictVaccineData.objects.get(lot__lotId__contains = lotId, district__name__contains = name)
            district_vaccine_obj.arrivalTimestamp = datetime.datetime.now()
            district_vaccine_obj.save()
            VaccineLot.objects.filter(lotId = lotId).update(status = "atDistrict")
            return redirect("district_dash",name)    
    return redirect("district_dash",name)



def get_ratio_center(district):
    count_of_vaccine_atDistrict_state=DistrictVaccineData.objects.filter(district=district, lot__status__contains = "atDistrict").count()
    center_obj=Center.objects.filter(district=district)
    ratio_dict={}
    if(count_of_vaccine_atDistrict_state==0):
        
        for center in center_obj.iterator():
            ratio_dict[center.name]=int(0)
        return ratio_dict
    population_dict={}
    min_value=sys.maxsize
    max_value=0
    for center in center_obj.iterator():
        population_dict[center.name]=int(center.population)
        if(center.population < min_value):
            min_value=center.population
        if(center.population > max_value):
            max_value=center.population
    population_ratio_dict={}
    sum_of_ratio=0
    if(min_value==0):
        min_value=1

    for center in center_obj.iterator():
        population_ratio_dict[center.name]=ceil(center.population/min_value)
        sum_of_ratio+=population_ratio_dict[center.name]

    # if(sum_of_ratio > count_of_vaccine_atDistrict_state):
    #     while(sum_of_ratio > count_of_vaccine_atDistrict_state):
    #         quantity_subtract=count_of_vaccine_atDistrict_state-sum_of_ratio
    #         sum_of_ratio=0
    #         count=0
    #         for key in population_ratio_dict:

    #             print(int(population_ratio_dict[key])>0,quantity_subtract<0,quantity_subtract,count<quantity_subtract)

    #             if(int(population_ratio_dict[key])>0 and count<abs(quantity_subtract)):
    #                 population_ratio_dict[key]-=1
    #                 count+=1
    #                 print(key)
    #                 print(population_ratio_dict)
    #             sum_of_ratio+=population_ratio_dict[key]
                # quantity_subtract=count_of_vaccine_atDistrict_state-sum_of_ratio
    ratio_multiplication_factor = count_of_vaccine_atDistrict_state / sum_of_ratio


    # logger.info(ratio_multiplication_factor)

    for center in center_obj:
        ratio_dict[center.name] = floor(ratio_multiplication_factor * population_ratio_dict[center.name])
        if ratio_dict[center.name] == 0:
            ratio_dict[center.name] = ceil(ratio_multiplication_factor * population_ratio_dict[center.name])

    return ratio_dict




def send_to_center(request,name):
    if verify(request,"district",name):
        error = ""
        centers = Center.objects.filter(district__name__contains = name)
        if request.method == "POST":
            center_names = request.POST.getlist('centers')
            lot_quantities = request.POST.getlist('quantities')
            center_quantities = list(zip(center_names,lot_quantities))
            error = ""
            count = 0
            for center_name,lot_quantity in center_quantities:
                if(int(lot_quantity) > 0):
                    count = int(lot_quantity)
                    while count != 0:
                        lots_count = DistrictVaccineData.objects.filter(district__name__contains = name, lot__status__contains = "atDistrict").count()
                        if(lots_count > 0):
                            district_lot_obj = DistrictVaccineData.objects.filter(district__name__contains = name, lot__status__contains = "atDistrict")[0]
                            lot = district_lot_obj.lot
                            district_lot_obj.departureTimestamp = datetime.datetime.now()
                            district_lot_obj.save()
                            VaccineLot.objects.filter(lotId = lot.lotId).update(status = "transitToCenter")
                            center = Center.objects.get(name = center_name)
                            center_vaccine_obj = CenterVaccineData.objects.create(lot = lot, center=center)
                            center_vaccine_obj.save()
                            count -= 1
                        else:
                            error = "Quantities were assigned upto center: " + center_name 
                            break

        ratio=get_ratio_center(District.objects.get(name = name))
        ratio_list=[]
        count_list=[]
        for center in centers:
            count_list.append(CenterVaccineData.objects.filter(center=center, lot__status__contains = "atCenter").count())
            ratio_list.append(ratio[center.name])

        

        quantity_available = DistrictVaccineData.objects.filter(district__name__contains = name, lot__status__contains = "atDistrict").count()
        context = {"name":name,"centers":zip(centers,zip(ratio_list,count_list)),"quantity_available":quantity_available,"error":error}
        return render(request,"send_to_center.html",context)
    return redirect("district_dash",name)


@login_required
def center_dash(request,name):
    if name=="":
        return redirect('dashboard')
    if verify(request,"center",name):
        center_obj=Center.objects.get(name=name)
        #dist = AccessControlListDistrict.objects.get(person = request.user,district=district_obj[0])
        #dist_ID = dist.district
        vaccine_lots = CenterVaccineData.objects.filter(center = center_obj)
        return render(request,'center_dash.html',{'center_obj':center_obj,'vaccine_lots':vaccine_lots,'name':name})
    else:
        return redirect('dashboard')

@login_required
def updateMaxCountPerDate(request, name):
    if verify(request,"center",name):
        center_obj = Center.objects.filter(name=name)
        if(center_obj.exists()):
            if request.method == "POST":
                maxCountPerDate = request.POST["max_count"]
            center_obj.update(maxCountPerDate = maxCountPerDate)
            return redirect("center_dash",name)
    return redirect("center_dash",name)


@login_required
def updateArrivalTimeCenter(request, name, lotId):
    if verify(request,"center",name):
        center_vaccine_obj = CenterVaccineData.objects.filter(lot__lotId__contains = lotId, center__name__contains = name)
        if(center_vaccine_obj.exists()):
            center_vaccine_obj = CenterVaccineData.objects.get(lot__lotId__contains = lotId, center__name__contains = name)
            center_vaccine_obj.arrivalTimestamp = datetime.datetime.now()
            center_vaccine_obj.save()
            VaccineLot.objects.filter(lotId = lotId).update(status = "atCenter")
            return redirect("center_dash",name)    
    return redirect("center_dash",name)

@login_required
def receiverVaccination(request, name):
    error = ""
    if(verify(request,'center',name)):
        if request.method == 'POST':
            aadharNumber = request.POST['aadharNumber']
            receiver_obj = Receiver.objects.filter( aadharNumber = aadharNumber)
            if(receiver_obj.exists()): 
                maxCountOfDosesPerLot = 500
                center_obj = Center.objects.filter(name = name)
                lots = VaccineLot.objects.filter(status = 'atCenter', centerVaccine__center__in = center_obj)
                if(lots.exists()):
                    for lot in lots:
                        countOfDosesConsumed = lot.countOfDosesConsumed
                        if(countOfDosesConsumed < maxCountOfDosesPerLot):
                            receiver_obj = Receiver.objects.get(aadharNumber = aadharNumber)
                            receiver_vaccination_obj = ReceiverVaccination.objects.create(lot = lot, receiver = receiver_obj)
                            receiver_vaccination_obj.save()
                            lot.countOfDosesConsumed = countOfDosesConsumed+1
                            lot.save()
                            break      
                else:
                    error = "Lot not available" 
            else:
                error = "Receiver does not exists"
            print(error)             
        return render(request,"recieverVaccination.html",{'name':name,'error':error})
    return redirect("dashboard")





def registerForVaccinationDistrictForm(request):
    districts = District.objects.all().order_by("name")
    ########
    district_centers = []
    centers = Center.objects.all()
    for district in districts:
        for center in centers:
            if(center.district.name == district.name):
                district_centers.append(district.name + "-" +center.name)
    if request.method == "POST":
        district_center = request.POST["district_center"]
        district_center_name = str(district_center).split("-")
        district_name = district_center_name[0]
        center_name = district_center_name[1]
        return redirect("registerForVaccination",district_name,str(center_name))
    context = {"district_centers":district_centers}
    return render(request,"registerForVaccinationDistrictForm.html",context)


def registerForVaccination(request,district_name,center_name):
    
    error = ""
    if request.method == "POST":
        if Center.objects.filter(name = center_name).exists():
            center = Center.objects.get(name = center_name)
            aadharNumber = request.POST["aadharNumber"]
            if Receiver.objects.filter(aadharNumber = aadharNumber).exists():
                error = "Registration with the aadhar number already exists"
            else:
                full_name = request.POST["name"]
                contactNumber = request.POST["contactNumber"]
                address = request.POST["address"]
                appointment_date = request.POST["appointment_date"]
                reciever_obj = Receiver.objects.create(aadharNumber = aadharNumber, center = center , name = full_name, contactNumber = contactNumber, address = address, appointmentDate = appointment_date)
                reciever_obj.save()
                error = "Congratulations...You have been registered!!!"
        else:
            error = "Center does not exists"
         
    min_date = datetime.date.today()
    min_date = min_date + datetime.timedelta(days=7)
    while(True): 
        if(Receiver.objects.filter(center__name__contains = center_name, appointmentDate = min_date).count() < Center.objects.get(name = center_name).maxCountPerDate):
            break  
        min_date = min_date + datetime.timedelta(days=1)
    max_date = min_date + datetime.timedelta(days=7)
    blocked_dates = []
    start_date = min_date
    end_date = max_date
    delta = datetime.timedelta(days=1)
    while start_date <= end_date:
        if(Receiver.objects.filter(center__name__contains = center_name, appointmentDate = start_date).count() >= Center.objects.get(name = center_name).maxCountPerDate):
            blocked_dates.append(str(start_date))
        start_date += delta
    context={"district_name":district_name,"center_name":center_name,"min_date_for_registration":str(min_date),"error":error, "max_date_for_registration":str(max_date), 'blocked_dates':blocked_dates}
    return render(request,"registerForVaccination.html",context)


@login_required
def currentStatus(request):
    districts = District.objects.values()
    centers = Center.objects.values()
    lots = VaccineLot.objects.all()
    context = {"districts" : districts, "centers" : centers, "lots" : lots}
    return render(request, "status2.html", context)


#TODO verify function, clean templates
#TODO loggedin page where you can access all the places where you have access. If count equals to one admin of only one place
#go straight to that place

# TODO update uuid
# 