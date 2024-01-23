# occupancy_manager.py

from service.escapadarural_service import login_escapadarural, update_high_season_escapada, get_occupied_dates, \
    update_calendar_dates
from service.ical_service import load_ical, get_ical_dates
from manager.config_manager import load_config, save_config


def sync_ical_with_escapadarural(session, user_id, cottage_id):
    """
    Sincroniza los eventos de iCal con las fechas de disponibilidad de EscapadaRural.
    """
    config = load_config().get('escapadarural', {})
    accommodations = config.get('accommodations', [])

    # Buscar el alojamiento por código y actualizarlo
    accommodation_found = False
    for acc in accommodations:
        if acc.get('id') == cottage_id:
            accommodation_found = True
            if 'ical_url' in acc:
                try:
                    calendar = load_ical(acc['ical_url'])
                    ical_dates = get_ical_dates(calendar)
                    print(f"Eventos iCal para {acc.get('name')}: {ical_dates}")

                    rent_unit_id = acc.get('rent_unit_id')
                    escapada_dates = get_occupied_dates(session, user_id, cottage_id, rent_unit_id)
                    print(f"Fechas Escapada Rural para {acc.get('name')}: {escapada_dates}")
                    dates_to_close, dates_to_open = sync_dates(ical_dates, escapada_dates)
                    if dates_to_close or dates_to_open:
                        print(f"Fechas a cerrar: {dates_to_close}")
                        print(f"Fechas a abrir: {dates_to_open}")
                        update_calendar_dates(session, user_id, cottage_id, rent_unit_id, dates_to_close,
                                              dates_to_open)
                    else:
                        print("No hay cambios en las fechas.")

                except Exception as e:
                    print(f"Error: {e}")
            else:
                # Guardar URL de iCal si no está presente
                ical_url = input(f"Introduce la URL del iCal para {cottage_id}: ")
                acc['ical_url'] = ical_url
                print(f"URL de iCal guardada para {cottage_id}. Vuelve a ejecutar para sincronizar.")
            break

    if not accommodation_found:
        print(f"No se encontró el alojamiento con el código {cottage_id}.")

    if accommodation_found:
        save_config(config, 'escapadarural')


def sync_dates(ical_dates, portal_dates):
    # Convertimos las listas a conjuntos para facilitar la comparación
    ical_set = set(ical_dates)
    portal_set = set(portal_dates)

    # Las fechas para cerrar son las que están en iCal pero no en EscapadaRural
    dates_to_close = list(ical_set - portal_set)

    # Las fechas para abrir son las que están en EscapadaRural pero no en iCal
    dates_to_open = list(portal_set - ical_set)

    # Ordenamos las listas antes de devolverlas
    dates_to_close.sort()
    dates_to_open.sort()

    return dates_to_close, dates_to_open
