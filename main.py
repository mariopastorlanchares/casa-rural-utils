from manager.season_manager import set_special_seasons
from service.clubrural_service import login, get_accommodations, select_accommodation, get_current_rates, set_rates, \
    update_accommodation_dates
from manager.data_manager import add_festivos
from utils.scraping import scrape_and_process, scrape_festivos_espana


def main_menu():
    while True:
        print("1. Scrapear precios Clubrural")
        print("2. Obtener festivos España")
        print("3. Establecer tarifas Clubrural")
        print("4. Actualizar calendario de temporadas especiales Clubrural")
        print("5. Salir")
        choice = input("Elige una opción: ")

        if choice == '1':
            scrape_and_process()
        elif choice == '2':
            year = input("Introduce el año para el que deseas obtener los festivos: ")
            url = f'https://www.calendarr.com/espana/calendario-{year}/'
            festivos = scrape_festivos_espana(url, year)
            # Agregar los festivos al archivo JSON
            add_festivos(festivos)
        elif choice == '3':
            session = login()
            accommodations = get_accommodations(session)
            if accommodations:
                for accommodation in accommodations:
                    roomId = select_accommodation(session, accommodation['id'])
                    if roomId:
                        print(f"Realizando operaciones en el alojamiento: {accommodation['name']}")
                        current_rates = get_current_rates(session, roomId)
                        print(f"Tarifas actuales para {accommodation['name']}: {current_rates}")
                        new_rates = {}
                        for rate_name, rate_info in current_rates.items():
                            if isinstance(rate_info, dict):
                                # Para tarifas especiales con seasonId
                                current_price = rate_info['precio']
                                season_id = rate_info['seasonId']
                                new_price = input(
                                    f"Introduce la nueva tarifa para '{rate_name}' (Actual: {current_price}): ")
                                new_rates[rate_name] = {'precio': new_price, 'seasonId': season_id}
                            else:
                                # Para tarifas base como 'Dom-Jue' y 'Vie-Sab'
                                new_price = input(
                                    f"Introduce la nueva tarifa para '{rate_name}' (Actual: {rate_info}): ")
                                new_rates[rate_name] = new_price
                        set_rates(session, accommodation['id'], roomId, new_rates)
        elif choice == '4':
            session = login()
            if session is not None:
                accommodations = get_accommodations(session)
                for accommodation in accommodations:
                    roomId = select_accommodation(session, accommodation['id'])
                    current_rates = get_current_rates(session, roomId)
                    for rate_name, rate_info in current_rates.items():
                        if rate_name not in ['Vie-Sab', 'Dom-Jue']:
                            # Para tarifas especiales con seasonId
                            print(f"Estableciendo fechas para {rate_name} en {accommodation['name']}")
                            special_dates = set_special_seasons()
                            # Aquí se actualizarían las fechas especiales para el alojamiento en Clubrural
                            update_accommodation_dates(session, accommodation['id'], rate_info, rate_name,
                                                       special_dates)
        elif choice == '5':
            break


if __name__ == "__main__":
    main_menu()
