from django.urls import path
from . import views

urlpatterns = [
    path('', views.verify, name='verify'),
    path('investment_options_view/', views.investment_options_view, name='investment_options'),
    path('invest/<int:option_id>/', views.invest_view, name='invest'),
    path('status/<str:status>/', views.investment_status_view, name='investment_status'),
    path('verify/', views.verification_view, name='verification'),
    path('index/', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('service/', views.service, name='service'),
    path('why/', views.why, name='why'),
    path('team/', views.team, name='team'),
    path('setting/', views.setting, name='setting'),
    path('LogoutPage/', views.LogoutPage, name='logout'),
    path('reg/', views.reg, name='reg'),
    path('reset_profile/', views.reset_profile, name='reset_profile'),
]