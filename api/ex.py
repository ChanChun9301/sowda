import os
import django
import datetime

# 1. Django sazlamalaryny tanatmak (Skript hökmünde işledýän bolsaňyz)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings') # Proýektiň adyny ýazyň
django.setup()

# 2. Absolut import (Nokat ulanmaň!)
from api.models import Logist, Address, LogistCategory

# Bazadan gerek bolan baglanyşyklary alýarys
addr = Address.objects.first()
cat = LogistCategory.objects.first()

if not addr or not cat:
    print("Säwlik: Bazada iň az bir Address we LogistCategory bolmaly!")
else:
    data = [
        {"name": "Aşgabat-Mary ýük", "nirden": "Aşgabat", "where": "Mary", "price": 500, "bring": True},
        {"name": "Halkara gatnaw (Eýran)", "nirden": "Lutfabad", "where": "Aşgabat", "price": 2500, "bring": True},
        {"name": "Tiz poçta hyzmaty", "nirden": "Balkanabat", "where": "Mary", "price": 150, "bring": True},
        {"name": "Mebel göçürmek", "nirden": "Aşgabat", "where": "Aşgabat", "price": 300, "bring": True},
        {"name": "Daşoguz Sowatgyçly ulag", "nirden": "Daşoguz", "where": "Aşgabat", "price": 1200, "bring": True},
        {"name": "Türkmenabat gurluşyk haryt", "nirden": "Türkmenabat", "where": "Kerki", "price": 400, "bring": True},
        {"name": "Azyk harytlary (Lomaý)", "nirden": "Aşgabat", "where": "Balkanabat", "price": 800, "bring": True},
        {"name": "Hususy taksi hyzmaty", "nirden": "Mary", "where": "Aşgabat", "price": 100, "bring": False},
        {"name": "Tehnika daşama", "nirden": "Balkan", "where": "Daşoguz", "price": 1500, "bring": True},
        {"name": "Dokument eltip bermek", "nirden": "Aşgabat", "where": "Türkmenbaşy", "price": 50, "bring": True},
        {"name": "Galla we däne daşama", "nirden": "Mary", "where": "Balkan", "price": 1100, "bring": True},
        {"name": "Suw daşaýan ulag (Kamaz)", "nirden": "Änew", "where": "Änew", "price": 200, "bring": True},
        {"name": "Awto-ewakuator", "nirden": "Aşgabat", "where": "Mary", "price": 600, "bring": True},
        {"name": "Sowgat eltip bermek", "nirden": "Aşgabat", "where": "Aşgabat", "price": 30, "bring": True},
        {"name": "Gurluşyk çägesi", "nirden": "Bäherden", "where": "Aşgabat", "price": 450, "bring": True},
        {"name": "Halkara tirkeg (Türkiýe)", "nirden": "Stambul", "where": "Aşgabat", "price": 4500, "bring": True},
        {"name": "Ofis enjamlary", "nirden": "Aşgabat", "where": "Daşoguz", "price": 700, "bring": True},
        {"name": "Maliýe hasabatlary (Kuryer)", "nirden": "Türkmenabat", "where": "Aşgabat", "price": 80, "bring": True},
        {"name": "Ýeňil maşyn äkitmek", "nirden": "Balkanabat", "where": "Mary", "price": 900, "bring": True},
        {"name": "Öý haýwanlaryny daşama", "nirden": "Aşgabat", "where": "Mary", "price": 120, "bring": True},
    ]

    for i, item in enumerate(data):
        Logist.objects.create(
            name=item['name'],
            nirden=item['nirden'],
            where=item['where'],
            price=item['price'],
            bring=item['bring'],
            address=addr,
            category=cat,
            author=f"Ulanyjy_{i+1}",
            phone=f"+99365{100000 + i}",
            last_date=datetime.date.today() + datetime.timedelta(days=i+1),
            checked=True,
            vip=(i % 5 == 0)
        )
    print("20 sany Logist obýekti üstünlikli goşuldy!")