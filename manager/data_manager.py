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
    festivos.extend(data)
    # Ordenar los festivos por fecha
    festivos.sort(key=lambda x: x['fecha'])
    save_to_json(current_data, filename)