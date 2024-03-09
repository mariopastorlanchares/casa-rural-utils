import requests
from manager.config_manager import load_config, save_config
from manager.season_manager import set_special_seasons

BASE_URL = "https://www.casasrurales.net"


def login_casasrurales_net():
    session = requests.Session()
    login_url = f"{BASE_URL}/emp-Login.php"

    config = load_config().get('casasrurales_net', {})
    email = config.get('email')
    password = config.get('password')

    if not email or not password:
        email = input("Email de CasasRurales.net: ")
        password = input("Contraseña de CasasRurales.net: ")
        config.update({'email': email, 'password': password})
        save_config(config, 'casasrurales_net')

    payload = {
        'Mail': email,
        'Password': password
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.casasrurales.net/emp-Acceso.php",
        "Origin": "https://www.casasrurales.net",
    }

    response = session.post(login_url, data=payload, headers=headers)

    # Comprueba si el login fue exitoso verificando la presencia de una redirección a 'emp-Menu.php' en el texto de respuesta.
    if "emp-Menu.php" in response.text:
        print("Login exitoso en CasasRurales.net. Redirigiendo a emp-Menu.php")
        # Aquí podrías seguir con otra petición al URL de destino si es necesario, utilizando la misma sesión.
        menu_url = f"{BASE_URL}/emp-Menu.php"
        session.get(menu_url)  # Accede a la página de menú usando la sesión establecida
        # print(response.text)
        return session
    else:
        print("Error de login en CasasRurales.net")
        print(response.text)  # Mostrar la respuesta del texto puede dar más detalle sobre el error.
        return None


def set_closed_date(
        session,
        fecha,
        idc):
    calendario_url = f"{BASE_URL}/emp-MenuCalendarioRun2.php"
    params = {
        "fecha": fecha,
        "estado": 2,
        "idc": idc,
        "idu": 0,
        "issup": 0,
        "pre": 'undefined',
        "nminn": 'undefined',
        "ul": 1,
        "nu": 1,
        "idp": 28,
    }

    # Realizar petición GET con los parámetros.
    response = session.get(calendario_url, params=params)

    if response.status_code == 200:
        print("Fecha marcada como cerrada exitosamente.")
    else:
        print(f"Error al marcar la fecha como cerrada. Código de estado: {response.status_code}")


def set_closed_dates():
    session = login_casasrurales_net()
    special_dates = set_special_seasons()
    for date in special_dates:
        # Formatea la fecha según sea necesario para casasrurales.net
        formatted_date = date.strftime('%Y-%m-%d')
        # TODO obtener id de alojamiento
        accommodation_id = 54300
        set_closed_date(session, formatted_date, accommodation_id)
        print(f"Fecha {formatted_date} actualizada como temporada alta para el alojamiento {accommodation_id}")
