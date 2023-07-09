
from django.contrib import admin
from django.urls import include, path

from main_app.views import *

urlpatterns = [
   path('',home_view, name='home'),
   path('login/', login_view,name='login'),
	path('logout/', logout_view, name='logout'),
   path('signup/', signup_view,name='signup'),
   path('my-courses/', my_courses_view,name='my-courses'),
   path('course/<str:slug>', coursePage , name = 'coursepage'), 
   path('check-out/<str:slug>', checkout , name = 'check-out'),
   path('verify_payment', verifyPayment , name = 'verify_payment'),
]
