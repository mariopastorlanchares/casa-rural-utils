import re
import requests

from manager.config_manager import load_config, save_config

BASE_URL = "https://www.escapadarural.com"


def login_escapadarural():
    session = requests.Session()
    login_url = f"{BASE_URL}/propietario/acceso"
    headers = {}
    while True:
        config = load_config().get('escapadarural', {})
        username = config.get('username')
        password = config.get('password')
        if not username or not password:
            # Si no existen las credenciales, solicitarlas al usuario
            username, password = request_login_data()

        payload = {
            'signin[username]': username,
            'signin[password]': password,
            'signin[remember]': 'on'
        }

        response = session.post(login_url, data=payload, headers=headers, allow_redirects=False)
        if response.status_code == 302:
            first_redirect_url = response.headers.get('Location', '')
            if first_redirect_url.startswith('/'):
                first_redirect_url = f"{BASE_URL}{first_redirect_url}"

            response = session.get(first_redirect_url, headers=headers, allow_redirects=False)

            if response.status_code == 302:
                second_redirect_url = response.headers.get('Location', '')
                if second_redirect_url.startswith('/'):
                    second_redirect_url = f"{BASE_URL}{second_redirect_url}"

                response = session.get(second_redirect_url, headers=headers)

                if response.status_code == 200:
                    print("Redireccionado a la página del menú del propietario")
                    user_id_match = re.search(r'/propietario/(.+?)/menu', second_redirect_url)
                    if user_id_match:
                        user_id = user_id_match.group(1)
                        print(f"ID del propietario: {user_id}")
                        save_config({'username': username, 'password': password}, 'escapadarural')
                        return session, user_id
                    else:
                        print("No se pudo encontrar el ID del propietario en la URL")
                else:
                    print("Error al seguir la segunda redirección")
            else:
                print("URL de redirección intermedia no encontrada o no hay segunda redirección")
        else:
            save_config({}, 'escapadarural')
            print("Login failed. Please try again.")


def request_login_data():
    username = input("Usuario de EscapadaRural: ")
    password = input("Contraseña de EscapadaRural: ")
    return username, password


def update_high_season_escapada(session, dates):
    for date in dates:
        # Construye la URL con los parámetros adecuados para cada fecha
        url = f"{BASE_URL}/owner/season/calendar-update/rqaXmKen0ZLKkbLXlt3vo6OUlZL175bFrJ_UkseZraqXlKjr6peak6qmmQ?day={date}&operation=add"
        response = session.get(url)
        if response.status_code == 200:
            print(f"Temporada alta establecida para {date}")
        else:
            print(f"Error al establecer temporada alta para {date}: {response.status_code}")
