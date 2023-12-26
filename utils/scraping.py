import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

from config.config_manager import load_config, save_config


def scrape_and_process():
    # Solicitar datos del usuario
    config = load_config()['scraping']
    provincia = input("Introduce la provincia (por defecto '{}'): ".format(config.get('provincia', ''))) or config.get(
        'provincia', '')
    min_inquilinos = input(
        "Número mínimo de inquilinos (por defecto {}): ".format(config.get('min_inquilinos', '9'))) or config.get(
        'min_inquilinos', '9')
    max_inquilinos = input(
        "Número máximo de inquilinos (por defecto {}): ".format(config.get('max_inquilinos', '11'))) or config.get(
        'max_inquilinos', '11')

    casas_rurales = scrape_clubrural(provincia, min_inquilinos, max_inquilinos)

    # Crear DataFrame y ordenar por precio
    df = pd.DataFrame(casas_rurales)
    df = df.sort_values(by='precio_total')

    # Añadir índice como primera columna
    df.reset_index(drop=True, inplace=True)
    df.index += 1

    print("")
    print(df.to_string(index=True))

    media_precio_total = df['precio_total'].mean()
    media_precio_persona = df['precio_persona'].mean()
    print("")
    print(f"Media total/noche: {media_precio_total}")
    print(f"Media persona/noche: {media_precio_persona}")
    # Actualizar y guardar la configuración
    new_config = {'provincia': provincia, 'min_inquilinos': min_inquilinos, 'max_inquilinos': max_inquilinos}
    save_config(new_config, 'scraping')


def scrape_clubrural(provincia, min_inquilinos, max_inquilinos):
    casas_rurales = []
    pagina = 1

    while True:
        url = f'https://www.clubrural.com/busquedas/buscar-alojamiento.php?txtdestino={provincia}&destinoid=prov_34&fechaentrada=&fechasalida=&plazasMinimas={min_inquilinos}&adults={min_inquilinos}&childs=0&_pagi_pg={pagina}'
        print(f"Página: {pagina} ... ", end="", flush=True)
        response = requests.get(url)
        if response.status_code != 200:
            print("Error al acceder a la página")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        lista_casas = soup.find_all('li', class_='cottage')
        if not lista_casas:
            break  # No hay más casas, salir del bucle
        for casa in lista_casas:
            nombre = casa.find('h3').text.strip() if casa.find('h3') else 'Nombre no disponible'
            localidad = casa.find('small').text.strip() if casa.find('small') else 'Localidad no disponible'
            capacidad = re.search(r'(\d+) Personas máx\.', casa.text)
            capacidad = int(capacidad.group(1)) if capacidad else None
            if capacidad and capacidad > int(max_inquilinos):
                continue  # Descartar la casa si supera la capacidad máxima especificada
            precio_persona = re.search(r'(\d+)(?:€|€)', casa.text)
            precio_persona = int(precio_persona.group(1)) if precio_persona else None
            precio_total = precio_persona * capacidad if precio_persona and capacidad else 'No disponible'
            casas_rurales.append(
                {'nombre': nombre, 'localidad': localidad, 'capacidad': capacidad, 'precio_persona': precio_persona,
                 'precio_total': precio_total})

        print("OK")
        pagina += 1
    return casas_rurales


def scrape_festivos_espana():
    # Enviar solicitud HTTP para obtener el contenido de la página
    url = 'https://www.calendarr.com/espana/calendario-2024/'
    response = requests.get(url)
    if response.status_code != 200:
        print("Error al acceder a la página")
        return None

    # Analizar el contenido HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Buscar y extraer los días festivos
    festivos = []
    for mes in soup.find_all('span', class_='holiday-month'):
        mes_nombre = mes.text.strip()
        for festivo in mes.find_next('ul', class_='list-holidays').find_all('li', class_='list-holiday-box'):
            # Verificar si es un día festivo no laborable
            if festivo.find('div', class_='list-holiday-dayweek holiday'):
                dia = festivo.find('span', class_='holiday-day').text.strip()
                nombre = festivo.find('a', class_='holiday-name').text.strip() if festivo.find('a',
                                                                                               class_='holiday-name') else festivo.find(
                    'span', class_='holiday-name').text.strip()
                festivos.append({'mes': mes_nombre, 'dia': dia, 'nombre': nombre})

    # Imprimir los días festivos extraídos
    for festivo in festivos:
        print(f"{festivo['dia']} de {festivo['mes']}: {festivo['nombre']}")