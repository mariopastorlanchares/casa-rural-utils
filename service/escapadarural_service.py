import re
import requests
from bs4 import BeautifulSoup
from manager.config_manager import load_config, save_config

BASE_URL = "https://www.escapadarural.com"


def login_escapadarural():
    session = requests.Session()
    login_url = f"{BASE_URL}/propietario/acceso"
    headers = {}

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
                    # Obtener los nuevos datos de los alojamientos
                    new_accommodations_data = get_accommodations_ids(session, user_id)

                    # Cargar la configuración existente
                    escapadarural_config = load_config().get('escapadarural', {})
                    existing_accommodations = escapadarural_config.get('accommodations', [])

                    # Crear un diccionario con los ID de los alojamientos como claves para facilitar la búsqueda
                    existing_accommodations_dict = {acc['id']: acc for acc in existing_accommodations}

                    # Actualizar los alojamientos existentes o añadir nuevos
                    for new_acc in new_accommodations_data:
                        acc_id = new_acc['id']
                        if acc_id in existing_accommodations_dict:
                            # Actualizar la información del alojamiento existente
                            existing_accommodations_dict[acc_id].update(new_acc)
                        else:
                            # Añadir un nuevo alojamiento
                            existing_accommodations.append(new_acc)

                    # Guardar la configuración actualizada
                    escapadarural_config['accommodations'] = list(existing_accommodations_dict.values())
                    save_config(escapadarural_config, 'escapadarural')
                    return session, user_id
                else:
                    print("No se pudo encontrar el ID del propietario en la URL")
            else:
                print("Error al seguir la segunda redirección")
        else:
            print("URL de redirección intermedia no encontrada o no hay segunda redirección")
    else:
        print("Login failed. Please try again.")

    return None, None


def get_accommodations_ids(session, owner_id):
    url = f"{BASE_URL}/owner/{owner_id}/calendar-quick/rent-unit"
    response = session.get(url)
    if response.status_code != 200:
        print("Error al obtener los IDs de los alojamientos")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    cottage_select = soup.find('select', {'name': 'cottage'})
    if not cottage_select:
        print("No se encontró el select 'cottage'")
        return []

    accommodations = []
    for option in cottage_select.find_all('option'):
        acc_id = option['value']
        acc_name = option.text.strip()

        # Obtener el primer rent_unit_id para cada alojamiento
        rent_unit_id = get_first_rent_unit_id(session, owner_id, acc_id)
        accommodations.append({
            'id': acc_id,
            'name': acc_name,
            'rent_unit_id': rent_unit_id
        })

    return accommodations


def get_first_rent_unit_id(session, owner_id, cottage_id):
    url = f"{BASE_URL}/owner/{owner_id}/calendar-quick/rent-unit?select_cottage={cottage_id}"
    response = session.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        rent_unit_select = soup.find('select', {'name': 'rentUnit'})
        if rent_unit_select and rent_unit_select.find('option'):
            return rent_unit_select.find('option')['value']
    return None


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


def get_occupied_dates(session, user_id, cottage_id, rent_unit_id):
    """
    Extrae las fechas cerradas para un alojamiento y unidad alquilable específicos.

    :param session: Sesión activa con EscapadaRural
    :param user_id: ID del propietario
    :param cottage_id: ID del alojamiento
    :param rent_unit_id: ID de la unidad alquilable
    :return: Lista con las fechas cerradas
    """
    url = f"{BASE_URL}/owner/{user_id}/calendar-quick/rent-unit?select_cottage={cottage_id}&select_rentunit={rent_unit_id}"
    response = session.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Buscar el atributo x-data que contiene 'PCalendar' en su valor
        calendar_data_div = soup.find(lambda tag: tag.name == "div" and 'PCalendar' in tag.get('x-data', ''))

        if not calendar_data_div:
            print("No se encontró la información del calendario.")
            return []

        script_text = calendar_data_div['x-data']

        # Buscar el array de fechas cerradas en el texto del script
        dates_closed_match = re.search(r"dates_closed: \[([^\]]+)\]", script_text)
        if dates_closed_match:
            # Limpiar y convertir a lista
            dates_closed = dates_closed_match.group(1)
            # Eliminar comillas y dividir por coma para obtener una lista de fechas
            dates_closed_list = [date.strip().strip("'") for date in dates_closed.split(',')]
            print(dates_closed_list)
            return dates_closed_list
        else:
            print("No se encontraron fechas cerradas.")
            return []
    else:
        print(f"Error al obtener las fechas cerradas para el alojamiento {cottage_id} y la unidad {rent_unit_id}")
        return []

