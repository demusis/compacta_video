import os
import ffmpeg
from flask import Flask, request, send_file, after_this_request

app = Flask(__name__)

@app.route("/")
def index():
    return send_file('src/index.html')

@app.route('/compress', methods=['POST'])
def compress_video():
    if 'video' not in request.files:
        return 'No video file found', 400

    video = request.files['video']
    target_size_mb = int(request.form['target_size'])
    optimization_type = request.form['optimization_type']

    # Use a unique filename to avoid race conditions
    input_path = f"input_{video.filename}"
    output_path = f"compressed_{video.filename}"
    video.save(input_path)

    try:
        # Get video duration
        probe = ffmpeg.probe(input_path)
        duration = float(probe['format']['duration'])

        # Calculate target bitrates
        audio_bitrate = 128 * 1000  # 128 kbps
        target_total_bitrate = (target_size_mb * 1024 * 1024 * 8) / duration
        video_bitrate = int(target_total_bitrate - audio_bitrate)

        # Set up ffmpeg output options
        output_options = {
            'vcodec': 'libx264',
            'b:v': f'{video_bitrate}',
            'preset': 'medium',
            'acodec': 'aac',
            'b:a': f'{audio_bitrate}'
        }

        if optimization_type == 'compress_framerate':
            output_options['r'] = 24
        elif optimization_type == 'compress_resolution':
            output_options['vf'] = 'scale=-1:480'

        # Run ffmpeg
        (
            ffmpeg
            .input(input_path)
            .output(output_path, **output_options)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

        @after_this_request
        def cleanup(response):
            try:
                os.remove(input_path)
                os.remove(output_path)
            except OSError as e:
                # log the error, but don't crash
                print(f"Error cleaning up files: {e}")
            return response

        return send_file(output_path, as_attachment=True, download_name=f"compressed_{video.filename}")

    except ffmpeg.Error as e:
        # Clean up input file on error
        if os.path.exists(input_path):
            os.remove(input_path)
        return f'FFmpeg error:\n{e.stderr.decode()}', 500
    except Exception as e:
        # Clean up input file on other errors
        if os.path.exists(input_path):
            os.remove(input_path)
        return f'An error occurred: {str(e)}', 500

def main():
    app.run(port=int(os.environ.get('PORT', 80)))

if __name__ == "__main__":
    main()
