# occupancy_manager.py

from service.escapadarural_service import login_escapadarural, update_high_season_escapada, get_occupied_dates
from service.ical_service import load_ical, get_ical_events
from manager.config_manager import load_config, save_config


def sync_ical_with_escapadarural(accommodation_code):
    session, user_id = login_escapadarural()
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
                    print(f"Eventos iCal para {acc.get('name')}: {events}")

                    rent_unit_id = acc.get('rent_unit_id')
                    get_occupied_dates(session, user_id, accommodation_code, rent_unit_id)

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
