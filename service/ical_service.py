import requests
from icalendar import Calendar, Event
from datetime import datetime
from manager.config_manager import load_config, save_config
from datetime import datetime, timedelta


def load_ical(url_or_path):
    """
    Carga un archivo iCal desde una URL o un archivo local.
    """
    if url_or_path.startswith('http://') or url_or_path.startswith('https://'):
        response = requests.get(url_or_path)
        if response.status_code == 200:
            return Calendar.from_ical(response.text)
        else:
            raise Exception(f"Error al cargar el iCal desde la URL: {url_or_path}")
    else:
        with open(url_or_path, 'rb') as f:
            return Calendar.from_ical(f.read())


def get_ical_events(calendar):
    """
    Extrae los eventos de un objeto Calendar y los devuelve como una lista de fechas individuales
    a partir de la fecha actual en adelante.
    """
    today = datetime.now().date()  # Obtener la fecha actual
    occupied_dates = set()  # Usamos un conjunto para evitar fechas duplicadas

    for component in calendar.walk():
        if component.name == "VEVENT":
            start = component.get('dtstart').dt
            end = component.get('dtend').dt
            delta = (end - start).days

            # Agregar cada fecha del intervalo al conjunto si es hoy o en el futuro
            for i in range(delta):
                current_date = start + timedelta(days=i)
                if current_date >= today:
                    occupied_dates.add(current_date.isoformat())

    # Convertir el conjunto a una lista y ordenarla
    return sorted(list(occupied_dates))



if __name__ == "__main__":
    # Para propósitos de prueba
    sync_ical_with_escapadarural('CODIGO_CASA')
