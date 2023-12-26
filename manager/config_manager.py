import json

CONFIG_FILE = 'config.json'


def load_config():
    try:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {'scraping': {}}


def save_config(new_config, key):
    # Cargar la configuración existente o crear una nueva si no existe
    config = load_config()

    # Actualizar solo la sección 'scraping'
    config[key] = new_config

    # Guardar la configuración actualizada
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)
