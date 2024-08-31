from flask import Flask, request, send_file
import yt_dlp
from io import BytesIO
from contextlib import redirect_stdout
import ffmpeg

app = Flask(__name__)

def download_audio(url):
    options = {
        'format': 'bestaudio/best',
        'keepvideo': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '-',
        'noplaylist': True,
        'quiet': True,
        'noprogress': True
    }

    info = yt_dlp.YoutubeDL({'quiet': True, 'noprogress': True}).extract_info(
        url = url, download=False
    )

    buffer = BytesIO()

    with redirect_stdout(buffer):
        yt_dlp.YoutubeDL(options).download([url])

    buffer.seek(0)
    
    webm = ffmpeg.input('pipe:0')
    output_stream = ffmpeg.output(webm, 'pipe:1', format='mp3', acodec='libmp3lame')
    out, _ = ffmpeg.run(output_stream, input=buffer.getvalue(), capture_stdout=True, capture_stderr=True)

    output_buffer = BytesIO(out)
    output_buffer.seek(0)

    return output_buffer, info.get('title')



@app.route('/api/download')
def hello_world():
    url = request.args.get('url')

    audio, title = download_audio(url)

    return send_file(
        audio,
        download_name = f'{title}.mp3',
    )


if __name__ == '__main__':
    app.run() 