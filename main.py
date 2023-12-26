import pandas as pd

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
            scrape_festivos_espana()
            break
        elif choice == '3':
            break


if __name__ == "__main__":
    main_menu()
