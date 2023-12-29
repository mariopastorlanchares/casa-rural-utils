import re

import requests
from bs4 import BeautifulSoup

from manager.config_manager import save_config, load_config, update_accommodations

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
        new_accommodations = []

        for accommodation in soup.find_all('div', class_='kt-portlet'):
            name = accommodation.find('h3').find('a').text.strip()
            id_ = accommodation.find('h3').find('small').text.strip().split()[1]
            new_accommodations.append({'id': id_, 'name': name})
            print(f"{name} - {id_}")

        update_accommodations(new_accommodations)

        return new_accommodations
    else:
        print("Error accessing accommodations page")


def select_accommodation(session, accommodation_id):
    config = load_config().get('clubrural', {})
    accommodations = config.get('accommodations', [])
    """
    Selecciona un alojamiento específico en Clubrural usando su ID.

    :param session: Sesión actual de requests
    :param accommodation_id: ID del alojamiento a seleccionar
    :return: True si el alojamiento fue seleccionado correctamente, False en caso contrario
    """
    url = f'{BASE_URL}/intranet/preindex.php?id_aloj={accommodation_id}'
    response = session.get(url)

    if response.status_code == 200:
        print(f"Alojamiento con ID {accommodation_id} seleccionado correctamente.")
    else:
        print(f"Error al seleccionar el alojamiento con ID {accommodation_id}.")
        return False

        # Navegar a la página de tarifas
    tarifas_url = f'{BASE_URL}/intranet/tarifas.php'
    response = session.get(tarifas_url)

    if response.status_code == 200:
        # Extraer el roomId de la URL (asumiendo que se incluye como un parámetro)
        match = re.search(r'roomId=(\d+)', response.url)
        if match:
            roomId = match.group(1)
            print(f"roomId obtenido: {roomId}")
            # Actualizar la configuración con el nuevo roomId
            for acc in accommodations:
                if acc['id'] == accommodation_id:
                    acc['roomId'] = roomId
            config['accommodations'] = accommodations
            save_config(config, 'clubrural')
            return roomId
    else:
        print("Error al acceder a la página de tarifas.")
        return None


def get_current_rates(session, room_id):
    """
    Obtiene las tarifas actuales para un alojamiento específico.

    :param room_id:
    :param session: Sesión actual de requests
    :param accommodation_id: ID del alojamiento
    :return: Un diccionario con los detalles de las tarifas actuales
    """
    tarifas_url = f'{BASE_URL}/intranet/tarifas.php?roomId={room_id}&seasonId='
    response = session.get(tarifas_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        tarifas = {}
        # Extraer información de las tarifas base
        tarifas_base = soup.find_all('a', class_='Tarifas_base')
        for tarifa in tarifas_base:
            detalles = tarifa.text.strip().split('\n')
            if len(detalles) == 2:
                dias, precio = detalles
                tarifas[dias.strip()] = precio.strip()
        # Extraer información de las tarifas especiales
        tarifas_especiales = soup.find_all('div', class_='kt-widget2__item')
        for tarifa in tarifas_especiales:
            titulo = tarifa.find('a', class_='kt-widget2__title')
            if titulo:
                season_id = tarifa.find('a')['href'].split('seasonId=')[-1]
                detalles = titulo.text.strip().split('\n')
                if len(detalles) == 2:
                    nombre, precio = detalles
                    tarifas[nombre.strip()] = {'precio': precio.strip(), 'seasonId': season_id}
        return tarifas
    else:
        print("Error al acceder a la página de tarifas para el alojamiento ID:", room_id)
        return {}


def set_rates(session, accommodation_id, room_id, new_tariffs):
    """
    Establece una nueva tarifa para un alojamiento en Clubrural.

    :param accommodation_id:
    :param new_tariffs:
    :param session: Sesión actual de requests
    :param room_id: Room ID obtenido de la página de tarifas
    :return: True si la tarifa fue establecida correctamente, False en caso contrario
    """
    url = f'{BASE_URL}/intranet/controlador.tarifas.php'
    payload = {
        'alojId': accommodation_id,
        'id': '',
        'uniqId': '',
        'updateTarifaBase': room_id,
        'basetarifaDJ': new_tariffs.get('Dom-Jue', '')['precio'],
        'basetarifaVS': new_tariffs.get('Vie-Sab', '')['precio'],
        'baseDiasDJ': 2,
        # 1 significa 2 días, no sé por qué
        'baseDiasVS': 1,
    }
    # Agregar tarifas variables al payload
    for name, data in new_tariffs.items():
        if 'seasonId' in data:
            payload.update({
                'id': data['seasonId'],
                'name': name,
                'tarifa': data['precio'],
                'nnoches': 3,  # Ajusta según sea necesario
                'updateEspecial': data['seasonId']
            })

    response = session.post(url, data=payload)
    if response.status_code == 200:  # Verificar si este es el código de estado esperado para éxito
        print("Tarifa establecida correctamente para alojamiento:", accommodation_id)
        return True
    else:
        print("Error al establecer la tarifa para alojamiento:", accommodation_id)
        return False


def update_accommodation_dates(session, accommodation_id, rate_info, rate_name, special_dates):
    print(rate_info)
    url = f'{BASE_URL}/intranet/controlador.tarifas.php'
    season_id = rate_info['seasonId']
    # Construir el FormData
    form_data = {
        'alojId': accommodation_id,
        'id': season_id,
        'updateEspecial': season_id,
        'name': rate_name,
        'tarifa': rate_info['precio'],
        'nnoches': 3,  # Ajusta según sea necesario
    }

    # Agregar las fechas especiales
    for date in special_dates:
        form_data[f"dates[{date.strftime('%Y')}][{date.strftime('%m%d')}]"] = 1

    # Realizar la solicitud POST
    response = session.post(url, data=form_data)

    # Procesar y devolver la respuesta
    if response.status_code == 200:
        print("Fechas actualizadas correctamente")
    else:
        print(f"Hubo un error al establecer fechas {response}")

    return response
