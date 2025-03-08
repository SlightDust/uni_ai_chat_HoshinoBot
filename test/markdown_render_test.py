import os
import uuid
from flask import Flask, request, jsonify
import markdown2

app = Flask(__name__)

_current_dir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(_current_dir, 'md')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/md/render', methods=['POST'])
def render_markdown():
    if request.method == 'POST':
        markdown_content = request.get_data(as_text=True)
        if not markdown_content:
            return jsonify({'error': 'Markdown content is required', 'status':'error', 'url':''}), 400

        html_content = markdown2.markdown(markdown_content, extras=['fenced-code-blocks', 'tables', 'header-ids', 'toc', 'footnotes'])
        filename = str(uuid.uuid4()) + '.html'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        url = f'/md/{filename}'
        return jsonify({'url': url, 'status':'success', 'status':'ok'}), 200

@app.route('/md/<path:filename>', methods=['GET'])
def get_markdown_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 200
    else:
        return jsonify({'error': 'File not found', 'status':'error', 'url':''}), 404

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5921)