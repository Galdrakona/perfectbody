import json
import logging

import requests
import unicodedata
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from products.models import Product
from accounts.models import UserProfile, TrainersServices, Address
from django.http import JsonResponse


def clean_city_name(city):
    return ''.join(c for c in city if not c.isdigit()).strip()

def translate_weather_description(description):
    translations = {
        "Sunny": "slunečno",
        "Cloudy": "zataženo",
        "Partly cloudy": "částečně zataženo",
        "Mist": "mlha",
        "Rain": "déšť",
        "Snow": "sníh",
        "Thunderstorm": "bouřka",
        "Fog": "mlha",
        "Clear": "jasno",
        "Overcast": "převážně zataženo",
        "Light rain": "slabý déšť",
        "Heavy rain": "silný déšť",
        "Light snow": "slabé sněžení",
        "Heavy snow": "silné sněžení",
        "Showers": "přeháňky",
        "Drizzle": "mrholení",
        "Light drizzle": "slabé mrholení",
        "Heavy drizzle": "silné mrholení",
        "Hail": "kroupy",
        "Sleet": "déšť se sněhem",
        "Blizzard": "vánice",
        "Freezing rain": "mrznoucí déšť",
        "Windy": "větrno",
        "Breezy": "mírný vítr",
        "Gale": "bouřlivý vítr",
        "Hurricane": "hurikán",
        "Tornado": "tornádo",
    }
    return translations.get(description, description)

def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            current_condition = data['current_condition'][0]
            return {
                'city': city,
                'temperature': current_condition['temp_C'],
                'description': translate_weather_description(current_condition['weatherDesc'][0]['value']),
                'humidity': current_condition['humidity'],
            }
    except Exception as e:
        print(f"Chyba při získávání počasí: {e}")
    return None

def home(request):
    name_day = get_name_day()

    default_cities = ['Brno', 'Praha', 'Ostrava']
    weather_data = []

    if request.user.is_authenticated:
        address = Address.objects.filter(user=request.user).order_by('-id').first()
        if address:
            user_city = clean_city_name(address.city)
            weather = get_weather(user_city)
            if weather:
                weather_data.append(weather)

    if not weather_data:
        for city in default_cities:
            weather = get_weather(city)
            if weather:
                weather_data.append(weather)

    return render(request, 'home.html', {'name_day': name_day, 'weather_data': weather_data})

def get_name_day():
    try:
        response = requests.get('https://nameday.abalin.net/api/V1/today?country=cz')
        if response.status_code == 200:
            data = response.json()
            if 'nameday' in data and 'cz' in data['nameday']:
                return data['nameday']['cz']
            else:
                return "Není dostupné"
        else:
            return "API nedostupné"
    except Exception as e:
        print(f"Chyba při získávání jmenin: {e}")
        return "Chyba"

logger = logging.getLogger(__name__)


from django.http import JsonResponse
from django.contrib import messages

def add_to_cart(request, product_id):
    # Načtení košíku ze session (pokud neexistuje, vytvoří prázdný)
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    product = get_object_or_404(Product, id=product_id)

    # Kontrola, zda je produkt typu "service" a má schválené trenéry
    if product.product_type == 'service':
        has_approved_trainers = TrainersServices.objects.filter(service=product, is_approved=True).exists()
        if not has_approved_trainers:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': "Pro tuto službu nejsou k dispozici schválení trenéři."})
            messages.error(request, "Pro tuto službu nejsou k dispozici schválení trenéři.")
            return redirect('service', pk=product_id)

    # Kontrola skladové dostupnosti pro produkty typu "merchantdise"
    elif product.product_type == 'merchantdise':
        if product.available_stock() <= 0:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': "Produkt není skladem."})
            messages.error(request, "Produkt není skladem.")
            return redirect('product', pk=product_id)

    # Přidání produktu nebo služby do košíku
    if product_id_str in cart:
        if product.product_type == 'service' or cart[product_id_str]['quantity'] < product.available_stock():
            cart[product_id_str]['quantity'] += 1
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': "Nelze přidat více, než je dostupné množství."})
            messages.error(request, "Nelze přidat více, než je dostupné množství.")
            return redirect('product', pk=product_id)
    else:
        # Vytvoření nové položky v košíku
        cart[product_id_str] = {
            'product_name': product.product_name,
            'product_type': product.product_type,
            'price': float(product.price),
            'quantity': 1,
            'note': '',  # Inicializace poznámky
        }

    # Uložení košíku do session
    request.session['cart'] = cart
    request.session.modified = True

    # Odpověď na AJAX požadavek
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        total_items = sum(item['quantity'] for item in cart.values())
        total_price = sum(item['quantity'] * item['price'] for item in cart.values())
        return JsonResponse({
            'success': True,
            'cart_count': total_items,
            'cart_total': f"{total_price:.2f} Kč",
            'message': f"{product.product_name} byl přidán do košíku."
        })

    # Standardní odpověď na HTTP požadavek
    messages.success(request, f"{product.product_name} byl přidán do košíku.")
    return redirect('cart')


def view_cart(request):
    # Získání košíku ze session
    cart = request.session.get('cart', {})

    # Výpočet celkové ceny a jednotlivých částek
    for product_id, item in cart.items():
        item['total'] = item['quantity'] * item['price']
    total = sum(item['quantity'] * item['price'] for item in cart.values())

    # Zobrazení stránky košíku
    return render(request, 'cart.html', {"cart": cart, "total": total})

def remove_from_cart(request, product_id):
    # Získání košíku ze session
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        # Odebrání položky z košíku
        del cart[product_id_str]
        request.session['cart'] = cart

        messages.success(request, "Produkt byl odstraněn z košíku.")
    else:
        messages.error(request, "Produkt nebyl nalezen v košíku.")

    return redirect('cart')

def update_cart(request, product_id):
    # Získání košíku ze session
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        try:
            # Získání nového množství z POST dat
            new_quantity = int(request.POST.get('quantity', 1))
            if new_quantity > 0:
                # Aktualizace množství v košíku
                cart[product_id_str]['quantity'] = new_quantity
            else:
                # Odstranění položky, pokud je nové množství 0 nebo méně
                del cart[product_id_str]
        except ValueError:
            # Ošetření chybného vstupu
            messages.error(request, "Neplatná hodnota množství.")
            return redirect('cart')

    # Aktualizace session
    request.session['cart'] = cart
    messages.success(request, "Košík byl úspěšně aktualizován.")
    return redirect('cart')

def update_cart_ajax(request, product_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)

        # Získání produktu a jeho skladové zásoby
        product = get_object_or_404(Product, id=product_id)

        if product_id_str in cart:
            try:
                data = json.loads(request.body)
                new_quantity = int(data.get('quantity', 1))

                if new_quantity > 0:
                    # Kontrola skladové dostupnosti pouze pro produkty typu 'merchantdise'
                    if product.product_type == 'merchantdise' and new_quantity > product.available_stock():
                        return JsonResponse({
                            'success': False,
                            'error': f'Na skladě je k dispozici pouze {product.available_stock()} kusů.'
                        })

                    # Aktualizace množství v košíku
                    cart[product_id_str]['quantity'] = new_quantity
                    request.session['cart'] = cart

                    # Přepočet celkové ceny
                    total = sum(item['quantity'] * item['price'] for item in cart.values())
                    item_total = cart[product_id_str]['quantity'] * cart[product_id_str]['price']

                    return JsonResponse({
                        'success': True,
                        'item_total': f"{item_total:.2f} Kč",
                        'cart_total': f"{total:.2f} Kč"
                    })
                else:
                    # Odstranění položky z košíku, pokud je nové množství 0 nebo méně
                    del cart[product_id_str]
                    request.session['cart'] = cart

                    total = sum(item['quantity'] * item['price'] for item in cart.values())
                    return JsonResponse({'success': True, 'cart_total': f"{total:.2f} Kč"})

            except (ValueError, KeyError):
                return JsonResponse({'success': False, 'error': 'Neplatná hodnota množství.'})
        else:
            return JsonResponse({'success': False, 'error': 'Produkt nebyl nalezen v košíku.'})

    return JsonResponse({'success': False, 'error': 'Neplatný požadavek.'})

def user_profile_view(request, username):
    user = get_object_or_404(UserProfile, username=username)
    is_trainer = user.groups.filter(name='trainer').exists()

    if request.user.is_authenticated and request.user == user:
        return redirect('profile')

    if is_trainer:
        approved_services = TrainersServices.objects.filter(trainer=user, is_approved=True).select_related('service')
        return render(request, 'trainer.html', {
            'trainer': user,
            'approved_services': approved_services,
        })

    return render(request, 'user_profile.html', {
        'user': user,
        'is_trainer': is_trainer,
    })


def get_name_day():
    try:
        response = requests.get('https://nameday.abalin.net/api/V1/today?country=cz')
        if response.status_code == 200:
            data = response.json()
            if 'nameday' in data and 'cz' in data['nameday']:
                return data['nameday']['cz']
            else:
                return "Není dostupné"
        else:
            return "API nedostupné"
    except Exception as e:
        return f"Chyba: {e}"


def normalize_for_search(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text.lower())
        if unicodedata.category(c) != 'Mn'
    )

def search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'results': []})
        return render(request, 'search_results.html', {
            'query': query,
            'products': [],
            'services': [],
            'trainers': [],
        })

    normalized_query = normalize_for_search(query)

    # Vyhledávání produktů
    products = [
        {
            'id': product.id,
            'name': product.product_name,
            'description': product.product_short_description,
            'url': reverse('product', args=[product.id])
        }
        for product in Product.objects.filter(product_type='merchantdise')
        if normalized_query in normalize_for_search(product.product_name)
           or normalized_query in normalize_for_search(product.product_short_description or "")
    ]

    # Vyhledávání služeb
    services = [
        {
            'id': service.id,
            'name': service.product_name,
            'description': service.product_short_description,
            'url': reverse('service', args=[service.id])
        }
        for service in Product.objects.filter(product_type='service')
        if normalized_query in normalize_for_search(service.product_name)
           or normalized_query in normalize_for_search(service.product_short_description or "")
    ]

    # Vyhledávání trenérů se schválenými službami
    trainers = UserProfile.objects.filter(
        groups__name='trainer',
        services__is_approved=True
    ).distinct()

    filtered_trainers = [
        {
            'username': trainer.username,
            'name': f"{trainer.first_name} {trainer.last_name}",
            'description': trainer.trainer_short_description,
            'url': reverse('user_profile', args=[trainer.username])
        }
        for trainer in trainers
        if (
            normalized_query in normalize_for_search(trainer.username)
            or normalized_query in normalize_for_search(trainer.first_name)
            or normalized_query in normalize_for_search(trainer.last_name)
            or normalized_query in normalize_for_search(trainer.trainer_short_description or "")
        )
    ]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'results': {
                'products': products,
                'services': services,
                'trainers': filtered_trainers,
            }
        })

    return render(request, 'search_results.html', {
        'query': query,
        'products': products,
        'services': services,
        'trainers': filtered_trainers,
    })


def update_note_in_cart(request, product_id):
    if request.method == "POST":
        note = request.POST.get('note', '').strip()
        cart = request.session.get('cart', {})

        if str(product_id) in cart:
            cart[str(product_id)]['note'] = note  # Uložení poznámky
            request.session['cart'] = cart
            return JsonResponse({'success': True, 'note': note})

        return JsonResponse({'success': False, 'error': 'Produkt není v košíku.'})

    return JsonResponse({'success': False, 'error': 'Neplatná metoda.'})

logger = logging.getLogger(__name__)

def cart_data(request):
    cart = request.session.get('cart', {})  # Načítání košíku ze session
    logger.info(f"Cart data: {cart}")  # Výpis obsahu košíku do logu
    total = sum(item['quantity'] * item['price'] for item in cart.values())  # Výpočet celkové ceny

    cart_items = [
        {
            'id': product_id,
            'name': item['product_name'],
            'type': item['product_type'],
            'quantity': item['quantity'],
            'price': item['price'],
            'total': item['quantity'] * item['price'],
        }
        for product_id, item in cart.items()
    ]

    return JsonResponse({
        'items': cart_items,
        'cart_total': total,
        'cart_count': sum(item['quantity'] for item in cart.values())  # Počet položek
    })

def cart_data_navbar(request):
    cart = request.session.get('cart', {})
    cart_items = [
        {
            'id': product_id,
            'name': item['product_name'],
            'quantity': item['quantity'],
            'price': item['price'],
            'total': item['quantity'] * item['price'],
            # Přidání URL podle typu produktu
            'url': reverse('service', args=[product_id]) if item['product_type'] == 'service' else reverse('product', args=[product_id]),
        }
        for product_id, item in cart.items()
    ]
    cart_total = sum(item['quantity'] * item['price'] for item in cart.values())
    cart_count = sum(item['quantity'] for item in cart.values())

    return JsonResponse({
        'items': cart_items,
        'cart_total': cart_total,
        'cart_count': cart_count,
    })


def custom_404(request, exception):
    """Zpracování chyby 404 - Stránka nenalezena."""
    return render(request, '404.html', status=404)

def custom_500(request):
    """Zpracování chyby 500 - Interní chyba serveru."""
    return render(request, '500.html', status=500)

def custom_403(request, exception):
    """Zpracování chyby 403 - Přístup zamítnut."""
    return render(request, '403.html', status=403)

def custom_400(request, exception):
    """Zpracování chyby 400 - Špatný požadavek."""
    return render(request, '400.html', status=400)

def custom_503(request):
    """Volitelná funkce pro chybu 503 - Služba nedostupná."""
    return render(request, '503.html', status=503)

def custom_429(request):
    """Volitelná funkce pro chybu 429 - Příliš mnoho požadavků."""
    return render(request, '429.html', status=429)

def custom_408(request, exception):
    """Zpracování chyby 408 - Časový limit vypršel."""
    return render(request, '408.html', status=408)