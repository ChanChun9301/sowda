from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework import generics,filters,status,pagination
from .models import *
from .serializers import *
from .functions import hash_password
from django.contrib import messages
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

def index(request):
    author = request.GET.get('author')
    print(author)
    id=0
    token=False
    if author:
        try:
            check = UserProd.objects.get(author=author)
            if UserProd.objects.filter(author=author).exists():
                if (UserProd.objects.filter(checked=True)):
                    token = check.checked
                token = check.checked
        except UserProd.DoesNotExist:
            token=False
    else:
        token:False

    logist = Logist.objects.all()[:8]
    car = Car.objects.all()[:8]
    other = Other.objects.all()[:8]
    news = News.objects.all()[:8]
    service = Service.objects.all()[:8]
    elin = Elin.objects.all()[:8]
    carousel = CarouselImage.objects.all()   
    context = {
        'car':car,
        'logist':logist,
        'elin':elin,
        'other':other,
        'service':service,
        'news':news,
        'carousel':carousel,
        'token':token,
        'id':id,
    }
    return render(request,'index.html',context)

def logist(request):
    logist = Logist.objects.all()
    context = {
        'logist':logist,
    }
    return render(request,'logist.html',context)

def webUserCreate(request):
    if request.method == 'POST':
        author = request.POST.get('author')
        if author:
            author = author[-8:]
            print(author)
            try:
                # Create the user
                user = UserProd.objects.create(author=author)
                user.save()
                messages.success(request, 'Ulanyjy goşuldy!')
                return redirect('index')  # Redirect to the login page or another page
            except Exception as e:
                messages.error(request, str(e))
                return render(request, 'auth/login.html')
        else:
            messages.error(request, 'All fields are required.')
            return render(request, 'auth/login.html')
    return render(request, 'auth/login.html')

# class UserProdDetailView(APIView):
#     def post(self, request):
#         author = request.data.get('author')  # Use request.data for POST
#         user_id = request.data.get('user_id')  # Use request.data for POST

#         context = {
#             'token': False,
#             'id': None,
#         }

#         if author:
#             try:
#                 check = UserProd.objects.get(author=author, id=user_id)
#                 context['token'] = check.checked
#                 context['id'] = check.id

#                 # Check if any UserProd is checked
#                 if UserProd.objects.filter(checked=True).exists():
#                     return render(request, 'your_template.html', context)
                
#                 return render(request, 'your_template.html', context)
#             except UserProd.DoesNotExist:
#                 return render(request, 'your_template.html', context)
#         else:
#             return render(request, 'your_template.html', context)


def logist_detail(request,pk):
    logist = Logist.objects.get(pk=pk)
    images = ImageLogist.objects.filter(logist__pk=pk)
    context = {
        'logist':logist,
        'images':images,
    }
    print(images)
    return render(request,'logist_detail.html',context)

def car(request):
    car = Car.objects.all()
    context = {
        'car':car,
    }
    return render(request,'car.html',context)

def car_detail(request,pk):
    car = Car.objects.get(pk=pk)
    context = {
        'car':car,
    }
    return render(request,'car_detail.html',context)

def elin(request):
    elin = Elin.objects.all()
    context = {
        'elin':elin,
    }
    return render(request,'elin.html',context)

def elin_detail(request,pk):
    elin = Elin.objects.get(pk=pk)
    context = {
        'elin':elin,
    }
    return render(request,'elin_detail.html',context)

def service(request):
    service = Service.objects.all()
    context = {
        'service':service,
    }
    return render(request,'service.html',context)

def service_detail(request,pk):
    service = Service.objects.get(pk=pk)
    context = {
        'service':service,
    }
    return render(request,'service_detail.html',context)

def other(request):
    other = Other.objects.all()
    context = {
        'other':other,
    }
    return render(request,'other.html',context)

def other_detail(request,pk):
    other = Other.objects.get(pk=pk)
    context = {
        'other':other,
    }
    return render(request,'other_detail.html',context)

def news(request):
    news = News.objects.all()
    context = {
        'news':news,
    }
    return render(request,'news.html',context)

def news_detail(request,pk):
    news = News.objects.get(pk=pk)
    context = {
        'news':news,
    }
    return render(request,'news_detail.html',context)