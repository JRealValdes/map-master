import os
import subprocess
import re
import shutil
from datetime import datetime
from dotenv import load_dotenv


class MindMapService:
    def __init__(self):
        load_dotenv()
        self.project_name = os.getenv('PROJECT_NAME', 'Project')
        self.templates_directory = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "templates")
        self.markdowns_directory = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "markdowns")
        self.css_path = 'static/css/styles.css'

    def convert_markdown_to_html(self):
        try:
            result = subprocess.run(['node', 'convert_markdown_to_html.js'],
                                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(result.stdout.decode())
        except subprocess.CalledProcessError as e:
            print(f"Error converting markdown to HTML: {e.stderr.decode()}")

    def style_htmls(self):
        css_link = f'<link rel="stylesheet" type="text/css" href="/{self.css_path}">'

        # Define el directorio de respaldo con marca de tiempo
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        """
        backup_directory = os.path.join(
            self.templates_directory, f"backup_{timestamp}")

        # Crea el directorio de respaldo si no existe
        if not os.path.exists(backup_directory):
            os.makedirs(backup_directory)
        """
        # Copia los archivos originales al directorio de respaldo
        files = [f for f in os.listdir(
            self.templates_directory) if f.endswith('.html')]
        """
        for file in files:
            shutil.copy2(os.path.join(
                self.templates_directory, file), backup_directory)
        """
        # Itera sobre cada archivo y realiza la sustitución
        for file in files:
            file_path = os.path.join(self.templates_directory, file)

            # Lee el contenido del archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Agrega el enlace al CSS si no existe
            if css_link not in content:
                if '<head>' in content:
                    new_content = content.replace(
                        '<head>', f'<head>\n    {css_link}')
                elif '<head ' in content:  # Manejo de variaciones de la etiqueta <head>
                    new_content = re.sub(
                        r'(<head\s*.*?>)', r'\1\n    ' + css_link, content, flags=re.IGNORECASE)
                else:
                    new_content = re.sub(r'(<html\s*.*?>)', r'\1\n<head>\n    ' +
                                         css_link + '\n</head>', content, flags=re.IGNORECASE)
            else:
                new_content = content

            # Inserta el logo al final del body
            if '<img id="logo" src="static/assets/logo.png"' not in new_content:
                new_content = new_content.replace(
                    "</body>", '<img id="logo" src="/static/assets/logo.png" alt="Logo">\n</body>')

            # Guarda el contenido modificado en el archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

        print(
            f"Enlace al CSS actualizado y logo añadido en todos los archivos HTML. Respaldo creado en el directorio 'backup_{timestamp}'.")

    def generate_menu(self):
        # Define el template del sidebar con comillas consistentes
        sidebar_template = """
        <div id="sidebar">
          <h2>{0}</h2>
          {1}
        </div>
        """

        # Define el directorio de respaldo con marca de tiempo
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_directory = os.path.join(
            self.templates_directory, f"backup_{timestamp}")

        # Crea el directorio de respaldo si no existe
        """
        if not os.path.exists(backup_directory):
            os.makedirs(backup_directory)
        """
        # Copia los archivos originales al directorio de respaldo
        files = [f for f in os.listdir(
            self.templates_directory) if f.endswith('.html')]
        """
        for file in files:
            shutil.copy2(os.path.join(
                self.templates_directory, file), backup_directory)
        """
        # Construye el sidebar con los enlaces a todos los archivos HTML
        sidebar_links = ""
        for file in files:
            file_path = os.path.join(self.templates_directory, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r"<title>(.*?)</title>", content)
                if match:
                    title = match.group(1)
                else:
                    # Usa el nombre del archivo si no se encuentra <title>
                    title = os.path.splitext(file)[0]

            # Ajusta la ruta para Flask
            sidebar_links += f'<a href="/templates/{file}">{title}</a>\n'

        # Itera sobre cada archivo y realiza la modificación del título y la inserción del sidebar
        for file in files:
            file_path = os.path.join(self.templates_directory, file)

            # Lee el contenido del archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Define el nuevo contenido con el sidebar
            new_sidebar_links = re.sub(
                f'<a href="/templates/{file}"', f'<a href="/templates/{file}" class="active"', sidebar_links)
            sidebar = sidebar_template.format(
                self.project_name, new_sidebar_links)

            # Reemplaza o inserta el sidebar de manera robusta
            if '<div id="sidebar">' in content:
                new_content = re.sub(
                    r'<div id="sidebar">.*?</div>', sidebar, content, flags=re.DOTALL)
            else:
                new_content = re.sub(
                    r'(<body.*?>)', r'\1\n' + sidebar, content, flags=re.IGNORECASE)

            # Guarda el contenido modificado en el archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

        print(
            f"Título y menú actualizados en todos los archivos HTML. Respaldo creado en el directorio 'backup_{timestamp}'.")


# Ejemplo de uso
if __name__ == '__main__':
    service = MindMapService()
    service.convert_markdown_to_html()
    service.style_htmls()
    service.generate_menu()
