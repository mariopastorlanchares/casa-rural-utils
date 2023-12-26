import pandas as pd

from manager.data_manager import update_json, add_festivos
from utils.scraping import scrape_and_process, scrape_festivos_espana


def main_menu():
    while True:
        print("1. Scrapear precios Clubrural")
        print("2. Obtener festivos España")
        print("3. Salir")
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
            break


if __name__ == "__main__":
    main_menu()
