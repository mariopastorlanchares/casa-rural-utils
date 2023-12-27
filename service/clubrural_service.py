import requests
from bs4 import BeautifulSoup

from manager.config_manager import save_config, load_config

BASE_URL = 'https://www.clubrural.com'


def login():
    session = requests.Session()

    config = load_config().get('clubrural', {})
    username = config.get('username') or input("Usuario: ")
    password = config.get('password') or input("Contraseña: ")

    # Update only the login credentials in the configuration
    login_config = {'username': username, 'password': password}
    config.update(login_config)
    save_config(config, 'clubrural')

    payload = {
        'portal': 'Clubrural.com',
        'usuario': username,
        'contrasena': password,
        'remember': 'on'
    }

    login_url = f'{BASE_URL}/intranet/login.php'
    response = session.post(login_url, data=payload)

    if response.status_code in [200, 302]:
        print("Login successful")
        return session
    else:
        print("Login error")
        return None


def get_accommodations(session):
    url = f'{BASE_URL}/intranet/preindex.php'
    response = session.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        accommodations = []

        for accommodation in soup.find_all('div', class_='kt-portlet'):
            name = accommodation.find('h3').find('a').text.strip()
            id_ = accommodation.find('h3').find('small').text.strip().split()[1]
            accommodations.append({'id': id_, 'name': name})
            print(f"{name} - {id_}")
            # Update only the accommodations in the configuration
            config = load_config().get('clubrural', {})
            config['accommodations'] = accommodations
            save_config(config, 'clubrural')
    else:
        print("Error accessing accommodations page")
