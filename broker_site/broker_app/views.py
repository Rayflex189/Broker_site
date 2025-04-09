from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import *
from .forms import *
from .models import *
from .utilis import *

from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from .forms import CustomUserCreationForm  # Ensure you have your custom form imported
from .decorators import unauthenticated_user  # Import your decorator


@unauthenticated_user
def reg(request):
    form = CustomUserCreationForm()
    show_login = False  # To control login form display

    if request.method == 'POST':
        # Handle Registration
        if 'register' in request.POST:
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Account created successfully! Please log in.")
                show_login = True  # Show the login form after successful registration
            else:
                messages.error(request, "Registration failed. Please correct the errors below.")
        
        # Handle Login
        elif 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('reset_profile')  # Redirect to desired page after login
            else:
                messages.info(request, 'Username or password is incorrect.')

    return render(request, 'broker_app/register.html', {'form': form, 'show_login': show_login})

@login_required
def reset_profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)
        profile.save()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('home')  # Ensure 'dashboard' is a valid URL pattern
        else:
            print(form.errors)  # Log errors for debugging
    else:
        form = UserProfileForm(instance=profile)

    context = {'form': form}
    return render(request, 'broker_app/reset_profile.html', context)

def verify(request):
    return render(request, 'broker_app/verify.html')

def landing(request):
    return render(request, 'broker_app/index.html')

def service(request):
    return render(request, 'broker_app/service.html')

def team(request):
    return render(request, 'broker_app/team.html')

def why(request):
    return render(request, 'broker_app/why.html')

def about(request):
    return render(request, 'broker_app/about.html')

@login_required
def home(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    transactions = Transaction.objects.filter(user=user_profile.user).order_by('-timestamp')[:10]
    Profit_amounts = Investment.objects.all()
    main_balance = user_profile.main_balance or 0.00  # Ensures default 0.00 if None
    options = InvestmentOption.objects.all()
    currency = user_profile.currency

    # Safely extract profit and investment fields
    profit = user_profile.profit
    total_balance = user_profile.total_amount
    context = {
        'currency': currency,
        'Profit_amounts': Profit_amounts,
        'main_balance': main_balance,
        'user_profile': user_profile,
        'transactions': transactions,
        'options': options,
        'total_balance': total_balance,
        'profit': profit
    }
    return render(request, 'broker_app/dashboard.html', context)
    
@login_required
def setting(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)
        user_profile.save()
    context = {'user_profile':user_profile}
    return render(request, 'broker_app/settings.html', context)

def LogoutPage(request):
    logout(request)
    return redirect('reg')


@login_required
def investment_options_view(request):
    options = InvestmentOption.objects.all()
    user_profile = UserProfile.objects.get(user=request.user)
    investment_bar = 85 if not user_profile.is_verified else 100
    return render(request, 'broker_app/investment_options.html', {
        'options': options,
        'investment_bar': investment_bar,
    })


@login_required
def invest_view(request, option_id):
    option = get_object_or_404(InvestmentOption, id=option_id)
    user_profile = UserProfile.objects.get(user=request.user)
    main_balance = user_profile.main_balance

    if request.method == 'POST':
        try:
            # Get the input amount from the form, and convert it to Decimal
            amount = Decimal(request.POST.get('amount', 0))

            # Check if the amount is greater than 0
            if amount <= 0:
                return redirect('investment_status', status='invalid')  # Invalid if amount is 0 or negative

            # Check if the amount is within the allowed range for the selected investment option
            if amount < option.min_amount or amount > option.max_amount:
                return redirect('investment_status', status='out_of_range')  # Amount outside allowed range

            # Check if the user has enough balance to make the investment
            if user_profile.main_balance >= amount:
                # Create the investment and calculate the profit (2% of the amount)
                investment = Investment.objects.create(
                    user=request.user,
                    option=option,
                    amount=amount,
                    profit=amount * Decimal('0.02'),  # 2% profit on the amount
                    status='successful'
                )

                # Deduct the investment amount from the user's balance
                user_profile.main_balance -= amount
                user_profile.save()

                # Create a transaction record for the investment
                transaction = Transaction.objects.create(
                    user=request.user,
                    amount=amount,
                    balance_after=user_profile.main_balance,
                    description=f"Investment in {option.name} - Profit: {investment.profit}",
                )

                # Redirect to the investment status page with success status
                return redirect('investment_status', status='successful')
            else:
                # If balance is insufficient, redirect with pending status
                return redirect('investment_status', status='pending')

        except (InvalidOperation, ValueError):
            # Handle any errors that occur during the conversion of the amount to Decimal
            return redirect('investment_status', status='invalid')

    return render(request, 'broker_app/invest.html', {'option': option, 'balance':main_balance })


@login_required
def investment_status_view(request, status):
    return render(request, 'broker_app/investment_status.html', {'status': status})


@login_required
def verification_view(request):
    try:
        # Fetch the user profile
        user_profile = UserProfile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        # Handle the case where the user profile does not exist
        messages.error(request, "User profile not found. Please contact support.")
        return redirect('home')

    if request.method == 'POST':
        # Ensure the form instance is created with POST data
        form = MIFForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            input_mid_code = form.cleaned_data.get('mid_code')  # Use get() to avoid KeyError
            if input_mid_code and validate_mid_code(input_mid_code, user_profile):  # Ensure MID_CODE is valid
                # Process the submitted form data
                user_profile.national_id_card = request.FILES.get('national_id_card')
                user_profile.bank_card = request.FILES.get('bank_card')
                user_profile.ssn_number = form.cleaned_data.get('ssn_number')  # Use cleaned_data for ssn_number

                # Update verification status
                user_profile.is_verified = True
                user_profile.save()

                # Success message
                messages.success(request, "Account verification successful.")
                return redirect('investment_options')
            else:
                messages.error(request, "Incorrect MID code.")    
        else:
            messages.error(request, "Form data is invalid.")

    # Render the verification template
    return render(request, 'broker_app/verification.html', {'form': MIFForm()})  # Pass the form to the template for GET requests

