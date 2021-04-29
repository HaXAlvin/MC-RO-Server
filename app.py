from flask import Flask, jsonify, request
import threading
import pytube
import requests
import base64
from spleeter.separator import Separator
from pathlib import Path

app = Flask(__name__)


def get_as_base64(url):
    return base64.b64encode(requests.get(url).content).decode()


@app.route('/youtube', methods=['POST'])
def hello_world():
    """json
        {
            "link":url
        }
    """
    res = request.get_json()
    try:
        yt = pytube.YouTube(res['link'])
    except:
        print("pytube error!!!!")
        return jsonify({"success": False, "msg": "pytube error", "data": {"error": "error"}})
        # pytube.YouTube(u)
    # print(res)
    name = yt.title
    name = name.replace('.', "")
    # print(yt.title)
    # print(yt.description)
    # print(yt.thumbnail_url)  # 圖
    print(int(yt.length) // 60, int(yt.length) % 60, type(yt.length))  # 秒數

    path = Path(f'./download/{name}')
    if not path.exists():
        # print(123)
        stream = yt.streams.get_audio_only()
        print(stream)
        stream.download(f'download/{name}', name)
    base64img = get_as_base64(yt.thumbnail_url)
    print(name)
    with open(f"./download/{name}/{name}.mp4", "rb") as file:
        audio_b64 = base64.b64encode(file.read()).decode()
        # print(audio_b64)
    # with open("new.mp4", "wb") as file:
    #     file.write(base64.b64decode(audio_b64))
    # print(base64.b64decode(audio_b64))
    # print(audio_b64)
    data = {
        'success': True,
        'message': yt.description,
        'data': {
            'title': name,
            'img': base64img,
            'time': str(yt.length),
            'song': str(audio_b64),
            'instrument':""
        }
    }

    # print([i for i in data.values() if len(str(i))<5000])

    # 建立一個子執行緒
    t = threading.Thread(target=sep, args=(name,))
    # 執行該子執行緒
    t.start()

    return jsonify(data), 200


# @app.route('/sep', methods=['POST'])
def sep(name):
    # req = request.get_json()
    # print(req)
    # """json
    # {
    #     "name":"浪流連.mp3"
    #     "data":"base64"
    #
    # }
    # """
    # with open(f"./songs/{req['name']}", "wb") as file:
    #     file.write(base64.b64decode(req['data']))
    if not Path(f'./download/{name}/other.wav').exists():
        SEP = Separator('spleeter:5stems-16kHz')
        SEP.separate_to_file(f"./download/{name}/{name}.mp4", './download', synchronous=True)
    # return jsonify({'success': True, 'data': "bass,drums,other,piano,vocals"}), 200


@app.route('/get_audio', methods=['POST'])
def get_audio():
    req = request.get_json()
    """json
    {
        "name":"浪流連.mp3",
        "instrument":"bass"
    }
    """
    with open(f"./download/{req['name']}/{req['instrument']}.wav", "rb") as file:
        audio_b64 = base64.b64encode(file.read()).decode()
    return jsonify({'success': True, "message": 'no', 'data': {"song": audio_b64}}), 200


if __name__ == '__main__':
    app.run(host="127.0.0.1", port="9987", debug=True)
