from service.clubrural_service import login, get_accommodations, select_accommodation, get_current_tariffs, set_tariffs
from manager.data_manager import add_festivos
from utils.scraping import scrape_and_process, scrape_festivos_espana


def main_menu():
    while True:
        print("1. Scrapear precios Clubrural")
        print("2. Obtener festivos España")
        print("3. Establecer tarifas Clubrural")
        print("4. Salir")
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
                        current_tariffs = get_current_tariffs(session, roomId)
                        print(f"Tarifas actuales para {accommodation['name']}: {current_tariffs}")
                        new_tariffs = {}
                        for tariff_name, tariff_info in current_tariffs.items():
                            if isinstance(tariff_info, dict):
                                # Para tarifas especiales con seasonId
                                current_price = tariff_info['precio']
                                season_id = tariff_info['seasonId']
                                new_price = input(
                                    f"Introduce la nueva tarifa para '{tariff_name}' (Actual: {current_price}): ")
                                new_tariffs[tariff_name] = {'precio': new_price, 'seasonId': season_id}
                            else:
                                # Para tarifas base como 'Dom-Jue' y 'Vie-Sab'
                                new_price = input(
                                    f"Introduce la nueva tarifa para '{tariff_name}' (Actual: {tariff_info}): ")
                                new_tariffs[tariff_name] = new_price
                        set_tariffs(session, accommodation['id'], roomId, new_tariffs)
        elif choice == '4':
            break


if __name__ == "__main__":
    main_menu()
