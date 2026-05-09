from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Car, ParkingSpot, Invoice, News, Term, Contact, Vacancy, Review, PromoCode, CompanyInfo, Client, Payment, Income
from datetime import datetime
from .forms import ClientRegistrationForm
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from calendar import month_name
import logging

logger = logging.getLogger(__name__)


def home(request):
    latest_news = News.objects.first()
    logger.info(f'Главная страница открыта')
    return render(request, 'parking_app/home.html', {'latest_news': latest_news})


def about(request):
    info = CompanyInfo.objects.first()
    return render(request, 'parking_app/about.html', {'info': info})


def privacy_policy(request):
    return render(request, 'parking_app/privacy.html')


def news_list(request):
    news = News.objects.all()
    return render(request, 'parking_app/news_list.html', {'news': news})


def news_detail(request, pk):
    news = get_object_or_404(News, pk=pk)
    return render(request, 'parking_app/news_detail.html', {'news': news})


def term_list(request):
    terms = Term.objects.all()
    return render(request, 'parking_app/term_list.html', {'terms': terms})


def contacts(request):
    contacts = Contact.objects.all()
    return render(request, 'parking_app/contacts.html', {'contacts': contacts})


def vacancy_list(request):
    vacancies = Vacancy.objects.all()
    return render(request, 'parking_app/vacancy_list.html', {'vacancies': vacancies})


def review_list(request):
    reviews = Review.objects.all()
    return render(request, 'parking_app/review_list.html', {'reviews': reviews})


@login_required
def add_review(request):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        text = request.POST.get('text', '').strip()
        
        logger.info(f'Пользователь {request.user.username} пытается добавить отзыв. Оценка: {rating}')
        
        # Валидация
        if not rating or rating not in ['1', '2', '3', '4', '5']:
            logger.warning(f'Неверная оценка от {request.user.username}: {rating}')
            return render(request, 'parking_app/add_review.html', {'error': 'Выберите оценку от 1 до 5'})
        
        if not text:
            logger.warning(f'Пустой отзыв от {request.user.username}')
            return render(request, 'parking_app/add_review.html', {'error': 'Текст отзыва не может быть пустым'})
        
        if len(text) < 3:
            logger.warning(f'Слишком короткий отзыв ({len(text)} символов) от {request.user.username}')
            return render(request, 'parking_app/add_review.html', {'error': 'Текст отзыва должен быть не менее 3 символов'})
        
        Review.objects.create(
            user=request.user,
            author_name=request.user.username,
            rating=rating,
            text=text
        )
        logger.info(f'Пользователь {request.user.username} успешно добавил отзыв')
        return redirect('reviews')
    
    return render(request, 'parking_app/add_review.html')


def promo_list(request):
    active = PromoCode.objects.filter(is_active=True)
    archived = PromoCode.objects.filter(is_active=False)
    return render(request, 'parking_app/promo_list.html', {'active': active, 'archived': archived})


@login_required
def car_list(request):
    cars = Car.objects.all()
    logger.info(f'Пользователь {request.user.username} просматривает список автомобилей')
    return render(request, 'parking_app/car_list.html', {'cars': cars})


@login_required
def car_detail(request, pk):
    car = get_object_or_404(Car, pk=pk)
    logger.info(f'Пользователь {request.user.username} просматривает авто {car.brand} {car.model}')
    return render(request, 'parking_app/car_detail.html', {'car': car})


def parking_spot_list(request):
    spots = ParkingSpot.objects.all()
    
    # Фильтрация по цене
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        spots = spots.filter(price_per_month__gte=min_price)
    if max_price:
        spots = spots.filter(price_per_month__lte=max_price)
    
    # Фильтрация по статусу занятости
    status = request.GET.get('status')
    if status == 'free':
        spots = spots.filter(is_occupied=False)
        logger.info(f'Фильтрация: показаны свободные места')
    elif status == 'occupied':
        spots = spots.filter(is_occupied=True)
        logger.info(f'Фильтрация: показаны занятые места')
    
    return render(request, 'parking_app/parking_spot_list.html', {'spots': spots})


@staff_member_required
def statistics(request):
    logger.info(f'Статистика открыта пользователем {request.user.username}')
    
    # ============================================================
    # 1. Клиент с самым большим долгом и дата последнего платежа
    # ============================================================
    top_debtor_data = (
        Invoice.objects.filter(is_paid=False)
        .values('client')
        .annotate(total_debt=Sum('amount'))
        .order_by('-total_debt')
        .first()
    )
    top_debtor = None
    if top_debtor_data:
        client = Client.objects.get(id=top_debtor_data['client'])
        last_payment = Payment.objects.filter(client=client).order_by('-payment_date').first()
        top_debtor = {
            'full_name': client.full_name,
            'debt': top_debtor_data['total_debt'],
            'last_payment_date': last_payment.payment_date if last_payment else 'Нет платежей'
        }

    # ============================================================
    # 2. Автомобили с несколькими владельцами
    # ============================================================
    multi_owner_cars = Car.objects.annotate(owners_count=Count('owners')).filter(owners_count__gt=1)
    multi_owner_count = multi_owner_cars.count()
    multi_owner_list = []
    for car in multi_owner_cars:
        multi_owner_list.append({
            'brand': car.brand,
            'model': car.model,
            'plate': car.license_plate,
            'owners_count': car.owners.count(),
            'owners': list(car.owners.all())
        })

    # ============================================================
    # 3. Период (для отчётов 3 и 4)
    # ============================================================
    period_days = request.GET.get('period_days', 30)
    try:
        period_days = int(period_days)
    except:
        period_days = 30
    start_date = timezone.now().date() - timedelta(days=period_days)

    # ============================================================
    # 4. Автомобиль с наименьшим долгом за период
    # ============================================================
    car_debts = (
        Car.objects.filter(invoice__date_incurred__gte=start_date, invoice__is_paid=False)
        .annotate(total_debt=Sum('invoice__amount'))
        .filter(total_debt__isnull=False)
        .order_by('total_debt')
    )
    min_debt_car = car_debts.first()
    min_debt_info = None
    if min_debt_car:
        min_debt_info = {
            'brand': min_debt_car.brand,
            'model': min_debt_car.model,
            'plate': min_debt_car.license_plate,
            'debt': min_debt_car.total_debt
        }

    # ============================================================
    # 5. Сумма долга за период (начисления - оплаты)
    # ============================================================
    total_invoiced = Invoice.objects.filter(date_incurred__gte=start_date).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
    total_paid = Payment.objects.filter(payment_date__gte=start_date).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
    net_debt = total_invoiced - total_paid

    # ============================================================
    # 6. Поиск по марке автомобиля (с сортировкой)
    # ============================================================
    brand_query = request.GET.get('brand', '')
    sort_by = request.GET.get('sort_by', 'brand')
    
    cars_by_brand = Car.objects.filter(brand__icontains=brand_query) if brand_query else []
    
    if brand_query:
        if sort_by == 'brand':
            cars_by_brand = cars_by_brand.order_by('brand')
        elif sort_by == 'model':
            cars_by_brand = cars_by_brand.order_by('model')
        elif sort_by == 'plate':
            cars_by_brand = cars_by_brand.order_by('license_plate')
    
    cars_by_brand_list = []
    for car in cars_by_brand:
        cars_by_brand_list.append({
            'brand': car.brand,
            'model': car.model,
            'plate': car.license_plate,
            'owners': list(car.owners.all())
        })

    # ============================================================
    # 7. Общая статистика
    # ============================================================
    total_cars = Car.objects.count()
    total_clients = Client.objects.count()
    total_spots = ParkingSpot.objects.count()
    occupied_spots = ParkingSpot.objects.filter(is_occupied=True).count()
    total_debt_all = Invoice.objects.filter(is_paid=False).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)

    context = {
        'top_debtor': top_debtor,
        'multi_owner_count': multi_owner_count,
        'multi_owner_list': multi_owner_list,
        'period_days': period_days,
        'min_debt_info': min_debt_info,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'net_debt': net_debt,
        'brand_query': brand_query,
        'sort_by': sort_by,
        'cars_by_brand_list': cars_by_brand_list,
        'total_cars': total_cars,
        'total_clients': total_clients,
        'total_spots': total_spots,
        'occupied_spots': occupied_spots,
        'total_debt_all': total_debt_all,
    }

    # ============================================================
    # 8. Данные для диаграммы
    # ============================================================
    free_spots = total_spots - occupied_spots
    chart_data = {
        'labels': ['Свободные', 'Занятые'],
        'data': [free_spots, occupied_spots],
        'colors': ['#28a745', '#dc3545']
    }
    context['chart_data'] = chart_data

    return render(request, 'parking_app/statistics.html', context)


def register_view(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f'Зарегистрирован новый пользователь: {user.username}')
            return redirect('home')
        else:
            logger.warning(f'Ошибка регистрации: {form.errors}')
    else:
        form = ClientRegistrationForm()
    return render(request, 'parking_app/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f'Пользователь {user.username} вошёл в систему')
            return redirect('home')
        else:
            logger.warning(f'Неудачная попытка входа: {request.POST.get("username")}')
    else:
        form = AuthenticationForm()
    return render(request, 'parking_app/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        logger.info(f'Пользователь {request.user.username} вышел из системы')
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    try:
        client = request.user.client
        cars = client.cars.all()
        invoices = client.invoices.all().order_by('-date_incurred')
        payments = client.payments.all().order_by('-payment_date')
        logger.info(f'Пользователь {request.user.username} открыл профиль')
    except Client.DoesNotExist:
        client = None
        cars = []
        invoices = []
        payments = []
    return render(request, 'parking_app/profile.html', {
        'client': client,
        'cars': cars,
        'invoices': invoices,
        'payments': payments,
    })


def is_employee(user):
    """Проверка, является ли пользователь сотрудником"""
    return hasattr(user, 'client') and user.client.is_employee


@user_passes_test(is_employee)
def employee_dashboard(request):
    """Панель сотрудника: видит всех клиентов, автомобили, счета, доходы"""
    logger.info(f'Сотрудник {request.user.username} открыл панель сотрудника')
    clients = Client.objects.all()
    cars = Car.objects.all()
    invoices = Invoice.objects.select_related('client', 'car').all()
    incomes = Income.objects.all()
    return render(request, 'parking_app/employee_dashboard.html', {
        'clients': clients,
        'cars': cars,
        'invoices': invoices,
        'incomes': incomes,
    })


# ============================================================
# КАЛЕНДАРЬ
# ============================================================

def calendar_view(request):
    """Отображение календаря в текстовом виде"""
    from calendar import monthcalendar, month_name
    from datetime import datetime
    
    today = datetime.now()
    year = request.GET.get('year', today.year)
    month = request.GET.get('month', today.month)
    
    try:
        year = int(year)
        month = int(month)
    except:
        year = today.year
        month = today.month
    
    cal = monthcalendar(year, month)
    month_title = month_name[month]
    
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    context = {
        'year': year,
        'month': month,
        'month_title': month_title,
        'calendar': cal,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
    }
    return render(request, 'parking_app/calendar.html', context)