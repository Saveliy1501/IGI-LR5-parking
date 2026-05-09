from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth.models import User
from datetime import date

# Валидатор телефона: +375 (29) XXX-XX-XX
phone_validator = RegexValidator(
    regex=r'^\+\d{3}\s\(\d{2}\)\s\d{3}-\d{2}-\d{2}$',
    message='Телефон должен быть в формате: +375 (29) XXX-XX-XX'
)


# ============================================
# МОДЕЛИ АВТОСТОЯНКИ
# ============================================

class Client(models.Model):
    """Клиент"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField('ФИО', max_length=200)
    birth_date = models.DateField('Дата рождения')
    phone = models.CharField('Телефон', max_length=20, validators=[phone_validator])
    is_employee = models.BooleanField('Сотрудник', default=False)

    
    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    
    def save(self, *args, **kwargs):
        if self.age < 18:
            raise ValueError('Клиент должен быть старше 18 лет')
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.full_name


class Car(models.Model):
    """Автомобиль"""
    license_plate = models.CharField('Госномер', max_length=15, unique=True)
    brand = models.CharField('Марка', max_length=50)
    model = models.CharField('Модель', max_length=50)
    owners = models.ManyToManyField(Client, related_name='cars')  # многие ко многим
    
    def __str__(self):
        return f"{self.brand} {self.model} ({self.license_plate})"


class ParkingSpot(models.Model):
    """Парковочное место"""
    spot_number = models.IntegerField('Номер места', unique=True, validators=[MinValueValidator(1)])
    price_per_month = models.DecimalField('Цена в месяц', max_digits=8, decimal_places=2)
    is_occupied = models.BooleanField('Занято', default=False)
    current_car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True)  # один ко многим
    
    def __str__(self):
        return f'Место №{self.spot_number}'


class Invoice(models.Model):
    """Счёт на оплату (долг)"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')    
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE)
    date_incurred = models.DateField('Дата начисления')
    amount = models.DecimalField('Сумма долга', max_digits=10, decimal_places=2)
    is_paid = models.BooleanField('Оплачено', default=False)
    paid_date = models.DateField('Дата оплаты', null=True, blank=True)
    
    def __str__(self):
        return f'Долг {self.amount} руб. - {self.client.full_name}'


class Income(models.Model):
    """Доход"""
    date = models.DateField('Дата')
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2)
    source = models.CharField('Источник', max_length=200)
    
    def __str__(self):
        return f'Доход {self.amount} руб.'
    
class Payment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payments')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()

    def __str__(self):
        return f"Payment {self.amount} by {self.client.full_name} on {self.payment_date}"


# ============================================
# МОДЕЛИ ДЛЯ СТРАНИЦ 
# ============================================

class CompanyInfo(models.Model):
    """О компании (таблица в БД)"""
    text = models.TextField('Текст о компании')
    video_url = models.URLField('Видео', blank=True)
    logo = models.ImageField('Логотип', upload_to='logos/', blank=True, null=True)
    requisites = models.TextField('Реквизиты', blank=True)
    
    def __str__(self):
        return 'О компании'


class News(models.Model):
    """Новости"""
    title = models.CharField('Заголовок', max_length=200)
    short_content = models.CharField('Краткое содержание', max_length=300)
    content = models.TextField('Полное содержание')
    image = models.ImageField('Картинка', upload_to='news/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class Term(models.Model):
    """Словарь терминов"""
    term = models.CharField('Термин', max_length=100)
    definition = models.TextField('Определение')
    added_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.term


class Contact(models.Model):
    """Контакты (сотрудники)"""
    full_name = models.CharField('ФИО', max_length=200)
    position = models.CharField('Должность', max_length=100)
    phone = models.CharField('Телефон', max_length=20, validators=[phone_validator])
    email = models.EmailField('Email')
    photo = models.ImageField('Фото', upload_to='employees/', blank=True, null=True)
    description = models.TextField('Описание выполняемых работ')
    
    def __str__(self):
        return self.full_name


class Vacancy(models.Model):
    """Вакансии"""
    title = models.CharField('Название', max_length=100)
    description = models.TextField('Описание')
    salary = models.CharField('Зарплата', max_length=100, blank=True)
    
    def __str__(self):
        return self.title


class Review(models.Model):
    """Отзывы"""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    author_name = models.CharField('Имя', max_length=100)
    rating = models.IntegerField('Оценка', choices=RATING_CHOICES)
    text = models.TextField('Текст отзыва')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.author_name} - {self.rating}⭐'


class PromoCode(models.Model):
    """Промокоды и купоны"""
    code = models.CharField('Код', max_length=50, unique=True)
    discount_percent = models.IntegerField('Скидка %')
    is_active = models.BooleanField('Действует', default=True)
    valid_from = models.DateField('Действует с')
    valid_to = models.DateField('Действует до')
    
    def __str__(self):
        return f'{self.code} ({self.discount_percent}%)'