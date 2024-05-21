from flask import Flask, request, render_template, jsonify, send_from_directory
from mindmap_service import MindMapService
from markdown_generator import MarkdownGenerator
import os
import re

app = Flask(__name__)
markdown_generator = MarkdownGenerator()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send_message', methods=['POST'])
def send_message():
    user_input = request.form['message']
    markdown, messages = markdown_generator.send_message(user_input)
    response = {'markdown': markdown, 'messages': messages}
    return jsonify(response)

# Nueva ruta para servir los archivos HTML generados


@app.route('/templates/<path:filename>')
def serve_page(filename):
    return send_from_directory('templates', filename)


@app.route('/get_maps', methods=['GET'])
def get_maps():
    maps = []
    for filename in os.listdir('templates'):
        if filename != 'index.html' and filename.endswith('.html'):
            with open(os.path.join('templates', filename), 'r', encoding='utf-8') as f:
                content = f.read()
                title_match = re.search(r"<title>(.*?)</title>", content)
                title = title_match.group(
                    1) if title_match else os.path.splitext(filename)[0]
                maps.append({'title': title, 'filename': filename})
    return jsonify({'maps': maps})


@app.route('/delete_map/<filename>', methods=['DELETE'])
def delete_map(filename):
    try:
        html_path = os.path.join('templates', filename)
        markdown_path = os.path.join(
            'markdowns', f"{os.path.splitext(filename)[0]}.md")

        if os.path.exists(html_path):
            os.remove(html_path)
        if os.path.exists(markdown_path):
            os.remove(markdown_path)
        mindmap_service = MindMapService()
        mindmap_service.generate_menu()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/regenerate_content', methods=['POST'])
def regenerate_content():
    try:
        mindmap_service = MindMapService()
        mindmap_service.convert_markdown_to_html()
        mindmap_service.style_htmls()
        mindmap_service.generate_menu()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=False)
