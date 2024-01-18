import requests
from icalendar import Calendar, Event
from datetime import datetime
from manager.config_manager import load_config, save_config


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
    Extrae los eventos de un objeto Calendar.
    """
    events = []
    for component in calendar.walk():
        if component.name == "VEVENT":
            events.append({
                "summary": str(component.get('summary')),
                "start": component.get('dtstart').dt,
                "end": component.get('dtend').dt
            })
    return events


def sync_ical_with_escapadarural(accommodation_code):
    """
    Sincroniza los eventos de iCal con las fechas de disponibilidad de EscapadaRural.
    """
    config = load_config().get('escapadarural', {})
    accommodations = config.get('accommodations', [])

    # Buscar el alojamiento por código y actualizarlo
    accommodation_found = False
    for acc in accommodations:
        if acc.get('id') == accommodation_code:
            accommodation_found = True
            if 'ical_url' in acc:
                try:
                    calendar = load_ical(acc['ical_url'])
                    events = get_ical_events(calendar)
                    print(f"Eventos iCal para {accommodation_code}: {events}")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                # Guardar URL de iCal si no está presente
                ical_url = input(f"Introduce la URL del iCal para {accommodation_code}: ")
                acc['ical_url'] = ical_url
                print(f"URL de iCal guardada para {accommodation_code}. Vuelve a ejecutar para sincronizar.")
            break

    if not accommodation_found:
        print(f"No se encontró el alojamiento con el código {accommodation_code}.")

    if accommodation_found:
        save_config(config, 'escapadarural')


if __name__ == "__main__":
    # Para propósitos de prueba
    sync_ical_with_escapadarural('CODIGO_CASA')
