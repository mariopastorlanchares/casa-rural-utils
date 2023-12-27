import os


def read_gitignore(gitignore_file):
    """
    Lee el archivo .gitignore y devuelve una lista de patrones a ignorar.
    """
    ignore_patterns = []
    with open(gitignore_file, 'r', encoding='utf-8') as file:
        ignore_patterns = [line.strip() for line in file if line.strip() and not line.startswith('#')]
    return ignore_patterns


def is_ignored(path, ignore_patterns):
    """
    Determina si la ruta dada debe ser ignorada basándose en los patrones de .gitignore.
    """
    for pattern in ignore_patterns:
        if pattern in path:
            return True
    return False


def gather_files(root_dir, extensions, ignore_patterns):
    """
    Recopila todos los archivos con las extensiones especificadas en el directorio dado y sus subdirectorios,
    excluyendo los patrones especificados.
    """
    files_to_collect = []
    venv_path = os.path.join(root_dir, '.venv')  # Ruta absoluta al directorio .venv

    for root, dirs, files in os.walk(root_dir):
        # Excluir el directorio .venv y otros directorios ignorados
        dirs[:] = [d for d in dirs if os.path.join(root, d) != venv_path and not is_ignored(os.path.join(root, d), ignore_patterns)]

        for file in files:
            file_path = os.path.join(root, file)
            if any(file.endswith(ext) for ext in extensions) and not is_ignored(file_path, ignore_patterns):
                files_to_collect.append(file_path)

    return files_to_collect



def write_contents_to_file(files_to_collect, output_file):
    """
    Escribe el contenido de cada archivo en el archivo de salida.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for file in files_to_collect:
            f.write(f"#### {file} ####\n\n")
            with open(file, 'r', encoding='utf-8') as file_content:
                f.write(file_content.read())
                f.write("\n\n")


def main():
    script_dir = os.path.dirname(__file__)  # Directorio donde se encuentra el script
    root_dir = os.path.join(script_dir, "../")  # Directorio raíz del proyecto
    extensions = ['.py', '.md']  # Extensiones de archivos a recopilar
    gitignore_file = os.path.join(root_dir, ".gitignore")  # Archivo .gitignore

    ignore_patterns = read_gitignore(gitignore_file)  # Leer .gitignore

    output_dir = os.path.join(root_dir, "tools/generated")  # Directorio de salida
    output_file = os.path.join(output_dir, "all_python_and_md_code.txt")  # Archivo de salida

    # Crear el directorio de salida si no existe
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files_to_collect = gather_files(root_dir, extensions, ignore_patterns)
    write_contents_to_file(files_to_collect, output_file)
    print(f"All Python and Markdown code has been written to {output_file}")


if __name__ == "__main__":
    main()
