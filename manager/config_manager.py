import json
import os

# Obtener el directorio del archivo actual (config_manager.py)
current_dir = os.path.dirname(__file__)
# Subir un nivel en la estructura de directorios para llegar al directorio raíz del proyecto
project_root = os.path.dirname(current_dir)
CONFIG_FILE = os.path.join(project_root, 'config.json')


def load_config():
    try:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {'scraping': {}, 'clubrural': {}}


def save_config(new_config, key):
    # Cargar la configuración existente o crear una nueva si no existe
    config = load_config()

    # Actualizar solo la sección 'scraping'
    config[key] = new_config

    # Guardar la configuración actualizada
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)


def update_accommodations(new_accommodations):
    config = load_config()
    clubrural_config = config.get('clubrural', {})
    existing_accommodations = clubrural_config.get('accommodations', [])

    accommodations_dict = {acc['id']: acc for acc in existing_accommodations}

    for acc in new_accommodations:
        if acc['id'] in accommodations_dict:
            accommodations_dict[acc['id']]['name'] = acc['name']
        else:
            accommodations_dict[acc['id']] = acc

    clubrural_config['accommodations'] = list(accommodations_dict.values())
    save_config(clubrural_config, 'clubrural')

