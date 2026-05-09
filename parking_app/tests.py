from django.test import TestCase, Client as DjangoClient
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from decimal import Decimal
from .models import Client, Car, ParkingSpot, Invoice, Payment, News, Review, PromoCode, CompanyInfo, Term, Contact, Vacancy, Income


# ============================================================
# ТЕСТЫ МОДЕЛЕЙ
# ============================================================

class ClientModelTest(TestCase):
    """Тесты модели Client"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client_obj = Client.objects.create(
            user=self.user,
            full_name='Тестов Тест Тестович',
            birth_date=date(1990, 1, 1),
            phone='+375 (29) 123-45-67'
        )
    
    def test_client_creation(self):
        """Тест создания клиента"""
        self.assertEqual(self.client_obj.full_name, 'Тестов Тест Тестович')
        self.assertEqual(self.client_obj.phone, '+375 (29) 123-45-67')
        self.assertEqual(self.client_obj.age, date.today().year - 1990)
    
    def test_client_str_method(self):
        """Тест метода __str__"""
        self.assertEqual(str(self.client_obj), 'Тестов Тест Тестович')
    
    def test_client_age_validation(self):
        """Тест возрастного ограничения 18+"""
        with self.assertRaises(ValueError):
            young_client = Client(
                full_name='Малолетний',
                birth_date=date(2015, 1, 1),
                phone='+375 (29) 111-11-11'
            )
            young_client.save()


class CarModelTest(TestCase):
    """Тесты модели Car"""
    
    def setUp(self):
        self.client1 = Client.objects.create(
            full_name='Владелец 1',
            birth_date=date(1980, 1, 1),
            phone='+375 (29) 111-11-11'
        )
        self.client2 = Client.objects.create(
            full_name='Владелец 2',
            birth_date=date(1985, 1, 1),
            phone='+375 (29) 222-22-22'
        )
        self.car = Car.objects.create(
            license_plate='А123ВЕ77',
            brand='Toyota',
            model='Camry'
        )
        self.car.owners.add(self.client1, self.client2)
    
    def test_car_creation(self):
        """Тест создания автомобиля"""
        self.assertEqual(self.car.brand, 'Toyota')
        self.assertEqual(self.car.model, 'Camry')
        self.assertEqual(self.car.license_plate, 'А123ВЕ77')
    
    def test_car_str_method(self):
        """Тест метода __str__"""
        self.assertEqual(str(self.car), 'Toyota Camry (А123ВЕ77)')
    
    def test_car_multiple_owners(self):
        """Тест связи многие-ко-многим"""
        self.assertEqual(self.car.owners.count(), 2)
        self.assertIn(self.client1, self.car.owners.all())
        self.assertIn(self.client2, self.car.owners.all())


class ParkingSpotModelTest(TestCase):
    """Тесты модели ParkingSpot"""
    
    def setUp(self):
        self.spot = ParkingSpot.objects.create(
            spot_number=1,
            price_per_month=Decimal('100.00'),
            is_occupied=False
        )
    
    def test_parking_spot_creation(self):
        """Тест создания парковочного места"""
        self.assertEqual(self.spot.spot_number, 1)
        self.assertEqual(self.spot.price_per_month, Decimal('100.00'))
        self.assertFalse(self.spot.is_occupied)
    
    def test_parking_spot_str_method(self):
        """Тест метода __str__"""
        self.assertEqual(str(self.spot), 'Место №1')
    
    def test_parking_spot_filter_by_price(self):
        """Тест фильтрации по цене"""
        ParkingSpot.objects.create(spot_number=2, price_per_month=Decimal('200.00'))
        spots_under_150 = ParkingSpot.objects.filter(price_per_month__lte=150)
        self.assertEqual(spots_under_150.count(), 1)


class InvoiceModelTest(TestCase):
    """Тесты модели Invoice"""
    
    def setUp(self):
        self.client = Client.objects.create(
            full_name='Тестов Клиент',
            birth_date=date(1990, 1, 1),
            phone='+375 (29) 111-11-11'
        )
        self.car = Car.objects.create(
            license_plate='А123ВЕ77',
            brand='Toyota',
            model='Camry'
        )
        self.spot = ParkingSpot.objects.create(
            spot_number=1,
            price_per_month=Decimal('100.00')
        )
        self.invoice = Invoice.objects.create(
            client=self.client,
            car=self.car,
            parking_spot=self.spot,
            date_incurred=date(2026, 1, 1),
            amount=Decimal('100.00'),
            is_paid=False
        )
    
    def test_invoice_creation(self):
        """Тест создания счёта"""
        self.assertEqual(self.invoice.amount, Decimal('100.00'))
        self.assertFalse(self.invoice.is_paid)
    
    def test_invoice_str_method(self):
        """Тест метода __str__"""
        self.assertEqual(str(self.invoice), 'Долг 100.00 руб. - Тестов Клиент')


class ReviewModelTest(TestCase):
    """Тесты модели Review"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='reviewer', password='12345')
        self.review = Review.objects.create(
            user=self.user,
            author_name='reviewer',
            rating=5,
            text='Отличная автостоянка!'
        )
    
    def test_review_creation(self):
        """Тест создания отзыва"""
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.text, 'Отличная автостоянка!')
    
    def test_review_str_method(self):
        """Тест метода __str__"""
        self.assertEqual(str(self.review), 'reviewer - 5⭐')


class NewsModelTest(TestCase):
    """Тесты модели News"""
    
    def setUp(self):
        self.news = News.objects.create(
            title='Тестовая новость',
            short_content='Краткое содержание',
            content='Полный текст новости'
        )
    
    def test_news_creation(self):
        """Тест создания новости"""
        self.assertEqual(self.news.title, 'Тестовая новость')
        self.assertEqual(self.news.short_content, 'Краткое содержание')
    
    def test_news_str_method(self):
        """Тест метода __str__"""
        self.assertEqual(str(self.news), 'Тестовая новость')


class PromoCodeModelTest(TestCase):
    """Тесты модели PromoCode"""
    
    def setUp(self):
        self.promo = PromoCode.objects.create(
            code='TEST10',
            discount_percent=10,
            is_active=True,
            valid_from=date(2026, 1, 1),
            valid_to=date(2026, 12, 31)
        )
    
    def test_promo_creation(self):
        """Тест создания промокода"""
        self.assertEqual(self.promo.code, 'TEST10')
        self.assertEqual(self.promo.discount_percent, 10)
    
    def test_promo_str_method(self):
        """Тест метода __str__"""
        self.assertEqual(str(self.promo), 'TEST10 (10%)')


# ============================================================
# ТЕСТЫ ПРЕДСТАВЛЕНИЙ (VIEWS)
# ============================================================

class ViewsTest(TestCase):
    """Тесты представлений (views)"""
    
    def setUp(self):
        # ВАЖНО: используем DjangoClient, а не модель Client
        self.client = DjangoClient()
        
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.superuser = User.objects.create_superuser(username='admin', password='admin123', email='admin@test.com')
        
        # Создаём тестовые данные
        self.car = Car.objects.create(
            license_plate='ТЕСТ001',
            brand='TestBrand',
            model='TestModel'
        )
        self.spot = ParkingSpot.objects.create(
            spot_number=99,
            price_per_month=Decimal('50.00'),
            is_occupied=False
        )
        self.news = News.objects.create(
            title='Тестовая новость',
            short_content='Краткое содержание',
            content='Полный текст новости'
        )
    
    def test_home_page_status_code(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_about_page_status_code(self):
        """Тест страницы 'О компании'"""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
    
    def test_news_list_page_status_code(self):
        """Тест страницы списка новостей"""
        response = self.client.get(reverse('news_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_terms_page_status_code(self):
        """Тест страницы словаря терминов"""
        response = self.client.get(reverse('terms'))
        self.assertEqual(response.status_code, 200)
    
    def test_contacts_page_status_code(self):
        """Тест страницы контактов"""
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)
    
    def test_vacancies_page_status_code(self):
        """Тест страницы вакансий"""
        response = self.client.get(reverse('vacancies'))
        self.assertEqual(response.status_code, 200)
    
    def test_reviews_page_status_code(self):
        """Тест страницы отзывов"""
        response = self.client.get(reverse('reviews'))
        self.assertEqual(response.status_code, 200)
    
    def test_promocodes_page_status_code(self):
        """Тест страницы промокодов"""
        response = self.client.get(reverse('promocodes'))
        self.assertEqual(response.status_code, 200)
    
    def test_parking_spots_page_status_code(self):
        """Тест страницы парковочных мест"""
        response = self.client.get(reverse('spots'))
        self.assertEqual(response.status_code, 200)
    
    def test_car_list_requires_login(self):
        """Тест: список автомобилей требует авторизации"""
        response = self.client.get(reverse('cars'))
        # Должен быть редирект на страницу входа (302)
        self.assertEqual(response.status_code, 302)
    
    def test_car_list_authenticated(self):
        """Тест: авторизованный пользователь видит автомобили"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('cars'))
        self.assertEqual(response.status_code, 200)
    
    def test_car_detail_authenticated(self):
        """Тест: детальная страница автомобиля для авторизованного"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('car_detail', args=[self.car.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_parking_spot_list_filter_by_price(self):
        """Тест фильтрации парковочных мест по цене"""
        response = self.client.get(reverse('spots'), {'min_price': 30, 'max_price': 70})
        self.assertEqual(response.status_code, 200)
    
    def test_parking_spot_list_filter_by_status(self):
        """Тест фильтрации парковочных мест по статусу"""
        response = self.client.get(reverse('spots'), {'status': 'free'})
        self.assertEqual(response.status_code, 200)
    
    def test_statistics_access_for_admin(self):
        """Тест: статистику видит только админ"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 200)
    
    def test_statistics_access_for_regular_user(self):
        """Тест: обычный пользователь не видит статистику"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('statistics'))
        # Должен быть редирект (302) из-за staff_member_required
        self.assertEqual(response.status_code, 302)
    
    def test_register_page(self):
        """Тест страницы регистрации"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_page(self):
        """Тест страницы входа"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_profile_page_requires_login(self):
        """Тест: профиль требует авторизации"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
    
    def test_profile_page_authenticated(self):
        """Тест: авторизованный пользователь видит профиль"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
    
    def test_add_review_requires_login(self):
        """Тест: добавление отзыва требует авторизации"""
        response = self.client.get(reverse('add_review'))
        self.assertEqual(response.status_code, 302)
    
    def test_add_review_authenticated(self):
        """Тест: авторизованный пользователь может добавить отзыв"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('add_review'))
        self.assertEqual(response.status_code, 200)


# ============================================================
# ТЕСТЫ URL
# ============================================================

class URLTests(TestCase):
    """Тесты URL-маршрутов"""
    
    def setUp(self):
        self.client = DjangoClient()
    
    def test_home_url(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_url(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Редирект на логин
    
    def test_about_url(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)
    
    def test_news_url(self):
        response = self.client.get('/news/')
        self.assertEqual(response.status_code, 200)
    
    def test_contacts_url(self):
        response = self.client.get('/contacts/')
        self.assertEqual(response.status_code, 200)
    
    def test_vacancies_url(self):
        response = self.client.get('/vacancies/')
        self.assertEqual(response.status_code, 200)
    
    def test_terms_url(self):
        response = self.client.get('/terms/')
        self.assertEqual(response.status_code, 200)
    
    def test_promocodes_url(self):
        response = self.client.get('/promocodes/')
        self.assertEqual(response.status_code, 200)
    
    def test_cars_url_redirects_if_not_logged_in(self):
        """Список автомобилей редиректит на логин"""
        response = self.client.get('/cars/')
        self.assertEqual(response.status_code, 302)
    
    def test_login_url(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
    
    def test_register_url(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
    
    def test_logout_url(self):
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)  # Редирект после выхода


# ============================================================
# ТЕСТЫ ФОРМ
# ============================================================

class FormTests(TestCase):
    """Тесты форм"""
    
    def setUp(self):
        self.client = DjangoClient()
    
    def test_client_registration_form_valid(self):
        """Тест валидной формы регистрации"""
        from .forms import ClientRegistrationForm
        form_data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'full_name': 'Новый Пользователь',
            'phone': '+375 (29) 123-45-67',
            'birth_date': '1995-05-15',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        form = ClientRegistrationForm(data=form_data)
        if not form.is_valid():
            print(form.errors)  # Это покажет, какая именно ошибка
        self.assertTrue(form.is_valid())
    
    def test_client_registration_form_invalid_age(self):
        """Тест: возраст младше 18 лет — форма невалидна"""
        from .forms import ClientRegistrationForm
        form_data = {
            'username': 'younguser',
            'email': 'young@test.com',
            'full_name': 'Молодой Пользователь',
            'phone': '+375 (29) 123-45-67',
            'birth_date': '2010-05-15',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = ClientRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_client_registration_form_invalid_phone(self):
        """Тест: неправильный формат телефона"""
        from .forms import ClientRegistrationForm
        form_data = {
            'username': 'user',
            'email': 'user@test.com',
            'full_name': 'Тест Тест',
            'phone': '+375 (29) 123-45-6',  # неправильный формат (не хватает цифр)
            'birth_date': '1995-05-15',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = ClientRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_client_registration_form_missing_required_fields(self):
        """Тест: отсутствие обязательных полей"""
        from .forms import ClientRegistrationForm
        form_data = {
            'username': 'user',
            'email': 'user@test.com',
            # отсутствует full_name, phone, birth_date
            'password1': 'pass',
            'password2': 'pass'
        }
        form = ClientRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())