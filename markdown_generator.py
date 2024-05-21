from openai import OpenAI
from dotenv import load_dotenv
import os
import re
import hashlib
from mindmap_service import MindMapService

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
client = OpenAI(api_key=api_key)


class MarkdownGenerator:
    def __init__(self):
        self.thread = client.beta.threads.create()

    def send_message(self, user_input):
        # Verificar y cancelar cualquier ejecución activa antes de añadir un nuevo mensaje
        self.cancel_active_run()

        # Añadir un nuevo mensaje al hilo
        message = client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_input
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id,
            assistant_id=assistant_id
        )

        if run.status == 'completed':
            messages = client.beta.threads.messages.list(
                thread_id=self.thread.id
            )
            markdown = self.__extract_markdown(messages)
            if markdown and "---\nmarkmap" in markdown:
                # Guardar el markdown solo si contiene una cabecera y cuerpo válidos
                self.save_markdown(user_input, markdown)

            return markdown, self.__serialize_messages(messages)
        else:
            return None, run.status

    def cancel_active_run(self):
        runs = client.beta.threads.runs.list(thread_id=self.thread.id)
        for run in runs.data:
            if run.status == 'active':
                client.beta.threads.runs.cancel(run_id=run.id)

    def __extract_markdown(self, messages):
        text = ""
        for element in messages.data:
            for content in element.content:
                if content.type == 'text':
                    text += content.text.value + "\n"

        if not text:
            print("No text content found in messages.")
            return None

        # Extraer el contenido de la cabecera entre ---
        header_pattern = r"---\n([\s\S]*?)\n---"
        header_match = re.search(header_pattern, text)
        header = header_match.group(0) if header_match else ""

        # Extraer el contenido entre los delimitadores <!--midmap-start--> y <!--midmap-end-->
        body_pattern = r"<!--midmap-start-->([\s\S]*?)<!--midmap-end-->"
        body_match = re.search(body_pattern, text)
        body = body_match.group(1).strip() if body_match else ""

        if header and body:
            return f"{header}\n{body}"
        return text if text else None

    def __serialize_messages(self, messages):
        serialized_messages = []
        for element in messages.data:
            message_content = []
            for content in element.content:
                if content.type == 'text':
                    message_content.append(content.text.value)
            serialized_messages.append({
                'role': element.role,
                'content': message_content
            })
        return serialized_messages

    def save_markdown(self, user_input, markdown):
        # Reemplazar espacios en el nombre del archivo
        hash_object = hashlib.sha256(user_input.encode())
        filename = f"markdowns/{hash_object.hexdigest()}.md"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown)
            # Ejecutar los scripts en el orden especificado
        self.regenerate_content()

    def regenerate_content(self):
        service = MindMapService()
        service.convert_markdown_to_html()
        service.style_htmls()
        service.generate_menu()
