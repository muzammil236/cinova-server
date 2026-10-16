import os
import requests
from flask import Flask, Response, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8989443537:AAEVGcwgZXQNmluwx0a23JkTG9sxGm1Yz_w')
TELEGRAM_API = f'https://api.telegram.org/bot{BOT_TOKEN}'
TELEGRAM_FILE = f'https://api.telegram.org/file/bot{BOT_TOKEN}'

@app.route('/')
def home():
    return jsonify({'status': 'CINOVA Server Running'})

def stream_by_file_id(file_id):
    try:
        file_res = requests.get(f'{TELEGRAM_API}/getFile', params={'file_id': file_id}, timeout=15)
        file_json = file_res.json()
        if not file_json.get('ok'):
            return jsonify({'error': 'File nahi mili'}), 404
        file_path = file_json['result']['file_path']
        file_url = f'{TELEGRAM_FILE}/{file_path}'
        range_header = request.headers.get('Range')
        headers = {'Range': range_header} if range_header else {}
        tg_response = requests.get(file_url, headers=headers, stream=True, timeout=30)
        def generate():
            for chunk in tg_response.iter_content(chunk_size=65536):
                if chunk:
                    yield chunk
        resp_headers = {
            'Content-Type': tg_response.headers.get('Content-Type', 'video/mp4'),
            'Accept-Ranges': 'bytes',
            'Access-Control-Allow-Origin': '*',
        }
        if 'Content-Length' in tg_response.headers:
            resp_headers['Content-Length'] = tg_response.headers['Content-Length']
        if 'Content-Range' in tg_response.headers:
            resp_headers['Content-Range'] = tg_response.headers['Content-Range']
        return Response(generate(), status=206 if range_header else 200, headers=resp_headers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/file/<file_id>')
def stream_file(file_id):
    return stream_by_file_id(file_id)

@app.route('/url/<file_id>')
def get_url(file_id):
    try:
        file_res = requests.get(f'{TELEGRAM_API}/getFile', params={'file_id': file_id}, timeout=15)
        file_json = file_res.json()
        if not file_json.get('ok'):
            return jsonify({'error': 'File nahi mili'}), 404
        file_path = file_json['result']['file_path']
        return jsonify({'ok': True, 'url': f'{TELEGRAM_FILE}/{file_path}',
                        'stream_url': f"{request.host_url}file/{file_id}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
