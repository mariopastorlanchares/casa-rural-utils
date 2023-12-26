import json


def save_to_json(data, filename='data.json'):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


def load_from_json(filename='data.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def update_json(data, section, filename='data.json'):
    current_data = load_from_json(filename)
    current_data[section] = data
    save_to_json(current_data, filename)


def add_festivos(data, filename='data.json'):
    current_data = load_from_json(filename)
    festivos = current_data.setdefault('festivos', [])

    # Convertir la lista existente de festivos en un diccionario para evitar duplicados
    festivos_dict = {festivo['fecha']: festivo for festivo in festivos}

    # Añadir o actualizar los festivos
    for festivo in data:
        festivos_dict[festivo['fecha']] = festivo

    # Convertir el diccionario de vuelta a una lista y ordenarla
    festivos_ordenados = list(festivos_dict.values())
    festivos_ordenados.sort(key=lambda x: x['fecha'])

    # Guardar los festivos actualizados
    current_data['festivos'] = festivos_ordenados
    save_to_json(current_data, filename)
