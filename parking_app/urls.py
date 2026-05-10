from django.urls import path, re_path
from . import views
from . import api_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('news/', views.news_list, name='news_list'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('terms/', views.term_list, name='terms'),
    path('contacts/', views.contacts, name='contacts'),
    path('vacancies/', views.vacancy_list, name='vacancies'),
    path('reviews/', views.review_list, name='reviews'),
    path('reviews/add/', views.add_review, name='add_review'),
    path('promocodes/', views.promo_list, name='promocodes'),
    re_path(r'^cars/$', views.car_list, name='cars'),
    re_path(r'^cars/(?P<pk>[1-9][0-9]{0,3})/$', views.car_detail, name='car_detail'),
    path('spots/', views.parking_spot_list, name='spots'),
    path('statistics/', views.statistics, name='statistics'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('api/', api_views.api_page, name='api_page'),
    path('calendar/', views.calendar_view, name='calendar'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)