import requests
from django.shortcuts import render
from django.core.cache import cache

def get_weather():
    """Погода в Минске (бесплатный API wttr.in)"""
    url = "https://wttr.in/Minsk?format=%C+%t+%w&lang=ru"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text
        return "Нет данных"
    except:
        return "Ошибка подключения"

def get_exchange_rates():
    """Курсы валют (бесплатный API floatrates.com)"""
    url = "https://www.floatrates.com/daily/usd.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'usd': round(data.get('byn', {}).get('rate', 0), 2),
                'eur': round(data.get('eur', {}).get('rate', 0) * data.get('byn', {}).get('rate', 1), 2),
                'rub': round(data.get('byn', {}).get('rate', 0) / data.get('rub', {}).get('rate', 1), 4),
                'updated': data.get('byn', {}).get('date', '')
            }
    except:
        pass
    return {'usd': 0, 'eur': 0, 'rub': 0, 'updated': ''}

def api_page(request):
    """Страница с API данными (кэш 1 час)"""
    weather = cache.get('weather')
    rates = cache.get('rates')
    
    if weather is None:
        weather = get_weather()
        cache.set('weather', weather, 3600)
    
    if rates is None:
        rates = get_exchange_rates()
        cache.set('rates', rates, 3600)
    
    return render(request, 'parking_app/api_page.html', {
        'weather': weather,
        'rates': rates,
    })