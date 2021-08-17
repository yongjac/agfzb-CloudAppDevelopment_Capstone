from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .restapis import get_dealers_from_cf, get_dealer_by_id_from_cf, get_dealer_reviews_from_cf, post_request
from .models import CarModel
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')

# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://4103a966.us-south.apigw.appdomain.cloud/djangoapp/api/dealership"
        # Get dealers from the URL
        context['dealership_list'] = get_dealers_from_cf(url)
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://4103a966.us-south.apigw.appdomain.cloud/djangoapp/api/review"
        dealer_url = "https://4103a966.us-south.apigw.appdomain.cloud/djangoapp/api/dealership"
        context['review_list'] = get_dealer_reviews_from_cf(url, dealer_id)
        dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id)
        if dealer:
            context['dealer'] = dealer[0]
        else:
            context['dealer'] = {'full_name': 'No dealer'}
        return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    if request.method == 'GET':
        context['dealer_id'] = dealer_id
        context['cars'] = CarModel.objects.filter(dealer_id=dealer_id)
        url = "https://4103a966.us-south.apigw.appdomain.cloud/djangoapp/api/dealership"
        dealer = get_dealer_by_id_from_cf(url, dealer_id)
        if dealer:
            context['dealer'] = dealer[0]
        else:
            context['dealer'] = {'full_name': 'No dealer'}
        return render(request, 'djangoapp/add_review.html', context)
    if request.method == "POST":
        user = request.user
        if user.is_authenticated:
            content = request.POST['content']
            car_id = int(request.POST['car'])
            car = get_object_or_404(CarModel, pk=car_id)
            purchase_date = request.POST['purchasedate']
            
            review = {}
            if 'purchasecheck' in request.POST:
                review["purchase"] = True
            else:
                review["purchase"] = False
            review["dealership"] = dealer_id
            review["review"] = content
            review["name"] = user.get_full_name()
            review['car_make'] = car.make.name
            review['car_model'] = car.name
            review['car_year'] = car.year.strftime("%Y")
            review['purchase_date'] = purchase_date
            
            json_payload = {}
            json_payload["review"] = review
            url = 'https://4103a966.us-south.apigw.appdomain.cloud/djangoapp/api/review'
            post_request(url, json_payload, dealerId=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

