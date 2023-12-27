from service.clubrural_service import login, get_accommodations
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
            get_accommodations(session)
        elif choice == '4':
            break


if __name__ == "__main__":
    main_menu()
