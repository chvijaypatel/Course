from django.shortcuts import render , redirect,HttpResponse
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from time import time
from django.contrib.auth import authenticate,login,logout
from django.core.paginator import *
from django.shortcuts import render, redirect
from django.http import JsonResponse, response
from django.core.mail import EmailMessage
from django.contrib import messages
from django.http import HttpResponse
from main_app.models import *

KEY_ID  = "rzp_test_26WYBJdjNWA64A"
KEY_SECRET  = "0AORmLYrdmWn4Pxvs0ai3EuH"
import razorpay
client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))

# Create your views here.


from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser == True:
                return redirect('/admin/')
            else:
                return redirect('/')
        else:
            return render(request, 'courses/login.html', {'error': 'Invalid credentials'})
    return render(request, 'courses/login.html')

@csrf_exempt
def logout_view(request):
    logout(request)
    return redirect('login')

@csrf_exempt
def home_view(request):
    courses=Course.objects.filter(active=True)
    return render(request, 'courses/home.html',{'courses': courses,})


@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            if not User.objects.filter(username=email).exists():
                user = User.objects.create_user(username=email,email=email, password=password)
                login(request, user)
                return redirect('/')
            else:
                error = 'Username is already taken.'
        else:
            error = 'Passwords do not match.'
    else:
        error = None
    
    return render(request, 'courses/signup.html', {'error': error})


	

@csrf_exempt
def logout_view(request):
	logout(request)
	return redirect('/')


@csrf_exempt
def my_courses_view(request):
    if UserCourse.objects.filter(user = request.user):
        user_courses=UserCourse.objects.filter(user = request.user)
        return render(request, 'courses/my_courses.html', {'user_courses': user_courses})
    else:
        error = 'No any course enrolled by you , Please go to home and enrolled the course !.'
	
        return render(request, 'courses/my_courses.html', {'error': error})


@csrf_exempt
def coursePage(request , slug):
    course = Course.objects.get(slug  = slug)
    serial_number  = request.GET.get('lecture')
    videos = course.video_set.all().order_by("serial_number")

    if serial_number is None:
        serial_number = 1 

    video = Video.objects.get(serial_number = serial_number , course = course)

    if (video.is_preview is False):

        if request.user.is_authenticated is False:
            return redirect("login")
        else:
            user = request.user
            try:
                user_course = UserCourse.objects.get(user = user  , course = course)
            except:
                return redirect("check-out" , slug=course.slug)
        
        
    context = {
        "course" : course , 
        "video" : video , 
        'videos':videos
    }
    return  render(request , template_name="courses/course_page.html" , context=context )    
    	

@csrf_exempt
@login_required(login_url='/login')
def checkout(request , slug):
    course = Course.objects.get(slug  = slug)
    user = request.user
    action = request.GET.get('action')
    order = None
    payment = None
    error = None
    try:
        user_course = UserCourse.objects.get(user = user  , course = course)
        error = "You are Already Enrolled in this Course"
    except:
        pass
    amount=None
    if error is None : 
        amount =  int((course.price - ( course.price * course.discount * 0.01 )) * 100)
   # if ammount is zero dont create paymenty , only save emrollment obbect 
    
    if amount==0:
        userCourse = UserCourse(user = user , course = course)
        userCourse.save()
        return redirect('my-courses')   
                # enroll direct
    if action == 'create_payment':

            currency = "INR"
            notes = {
                "email" : user.email, 
                "name" : f'{user.first_name} {user.last_name}'
            }
            reciept = f"codewithvirendra-{int(time())}"
            order = client.order.create(
                {'receipt' :reciept , 
                'notes' : notes , 
                'amount' : amount ,
                'currency' : currency
                }
            )

            payment = Payment()
            payment.user  = user
            payment.course = course
            payment.order_id = order.get('id')
            payment.save()


    
    context = {
        "course" : course , 
        "order" : order, 
        "payment" : payment, 
        "user" : user , 
        "error" : error
    }
    return  render(request , template_name="courses/check_out.html" , context=context )    

@csrf_exempt
def verifyPayment(request):
    if request.method == "POST":
        data = request.POST
        context = {}
        print(data)
        try:
            client.utility.verify_payment_signature(data)
            razorpay_order_id = data['razorpay_order_id']
            razorpay_payment_id = data['razorpay_payment_id']

            payment = Payment.objects.get(order_id = razorpay_order_id)
            payment.payment_id  = razorpay_payment_id
            payment.status =  True
            
            userCourse = UserCourse(user = payment.user , course = payment.course)
            userCourse.save()

            print("UserCourse" ,  userCourse.id)

            payment.user_course = userCourse
            payment.save()

            return redirect('my-courses')   

        except:
            return HttpResponse("Invalid Payment Details")
        
        
 
# 
