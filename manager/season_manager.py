import json
from datetime import datetime, timedelta

from manager.data_manager import load_from_json


def load_festivos(filename='data.json'):
    with open(filename, 'r') as file:
        data = json.load(file)
        return data.get('festivos', [])


def is_weekend(date):
    return date.weekday() in [4, 5, 6]  # Viernes, Sábado, Domingo


def is_bridge_day(date):
    return date.weekday() in [0, 3]  # Lunes, Jueves


from datetime import datetime, timedelta
from manager.data_manager import load_from_json


# ... is_weekend, is_bridge_day, group_dates_in_ranges ...

def set_special_seasons():
    festivos = load_from_json()['festivos']
    today = datetime.today().date()
    potential_date_ranges = []

    meses_agregados = {}  # {año: {'july': False, 'august': False}}

    # Primero, revisar y agregar july y august si es necesario
    for festivo in festivos:
        festivo_date = datetime.strptime(festivo['fecha'], "%Y-%m-%d").date()
        year = festivo_date.year

        if year not in meses_agregados:
            meses_agregados[year] = {'july': False, 'august': False}

        # Solo agregar july y august si estamos en una fecha anterior a estos meses en el año actual
        if year > today.year or (year == today.year and today.month < 7):
            if festivo_date.month >= 7 and not meses_agregados[year]['july']:
                potential_date_ranges.append((datetime(year, 7, 1).date(), datetime(year, 7, 31).date(), 'july'))
                meses_agregados[year]['july'] = True

        if year > today.year or (year == today.year and today.month < 8):
            if festivo_date.month >= 8 and not meses_agregados[year]['august']:
                potential_date_ranges.append((datetime(year, 8, 1).date(), datetime(year, 8, 31).date(), 'august'))
                meses_agregados[year]['august'] = True

    # Luego, procesar los festivos individuales
    for festivo in festivos:
        festivo_date = datetime.strptime(festivo['fecha'], "%Y-%m-%d").date()
        year = festivo_date.year
        if festivo_date < today or (festivo_date.month in [7, 8] and meses_agregados[year][festivo_date.strftime('%B').lower()]):
            continue

        festivo_name = festivo['nombre']
        potential_dates = []

        if is_weekend(festivo_date) or is_bridge_day(festivo_date):
            potential_dates.extend([
                festivo_date + timedelta(days=-1),
                festivo_date,
                festivo_date + timedelta(days=1)
            ])

        for date in potential_dates:
            potential_date_ranges.append((date, date, festivo_name))

    # Agrupar fechas en rangos
    date_ranges = group_dates_in_ranges(potential_date_ranges)

    confirmed_special_dates = []
    # Pedir confirmación al usuario para cada rango de fechas
    for start_date, end_date, festivo_name in date_ranges:
        date_range = f"{start_date.strftime('%Y-%m-%d')} hasta {end_date.strftime('%Y-%m-%d')}"
        response = input(f"Rango {date_range} (por festivo '{festivo_name}'). ¿Agregar como temporada alta? (s/n, 'detener' para finalizar): ")
        if response.lower() == 'detener':
            break
        if response.lower() == 's':
            while start_date <= end_date:
                confirmed_special_dates.append(start_date)
                start_date += timedelta(days=1)

    confirmed_special_dates = sorted(list(set(confirmed_special_dates)))

    return confirmed_special_dates




def group_dates_in_ranges(dates_with_names):
    if not dates_with_names:
        return []

    # Ordenar por fecha de inicio
    dates_with_names.sort(key=lambda x: x[0])

    grouped_ranges = []
    start, end, name = dates_with_names[0]

    for current_start, current_end, current_name in dates_with_names[1:]:
        if current_start == end + timedelta(days=1) and name == current_name:
            # Extender el rango actual
            end = current_end
        else:
            # Añadir el rango anterior y empezar uno nuevo
            grouped_ranges.append((start, end, name))
            start, end, name = current_start, current_end, current_name

    # Añadir el último rango
    grouped_ranges.append((start, end, name))

    return grouped_ranges

