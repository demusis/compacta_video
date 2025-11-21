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

    input_path = f"input_{video.filename}"
    output_path = f"compressed_{video.filename}"
    video.save(input_path)

    try:
        # Get original video properties
        probe = ffmpeg.probe(input_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream is None:
            return 'No video stream found in the file', 400

        duration = float(probe['format']['duration'])
        original_size_bytes = float(probe['format']['size'])
        target_size_bytes = target_size_mb * 1024 * 1024

        # Calculate the compression ratio, ensuring it's not greater than 1
        compression_ratio = target_size_bytes / original_size_bytes if original_size_bytes > 0 else 1
        compression_ratio = min(compression_ratio, 1.0)

        # Calculate target bitrates based on target size
        audio_bitrate = 128 * 1000  # 128 kbps
        target_total_bitrate = (target_size_bytes * 8) / duration
        video_bitrate = int(target_total_bitrate - audio_bitrate)

        if video_bitrate < 10000: # 10 kbps
            return f"Target size of {target_size_mb}MB is too small for a video of this duration.", 400

        # Base ffmpeg output options
        output_options = {
            'vcodec': 'libx264',
            'b:v': f'{video_bitrate}',
            'preset': 'medium',
            'acodec': 'aac',
            'b:a': f'{audio_bitrate}'
        }

        # Apply proportional optimization if selected
        if optimization_type == 'compress_framerate':
            original_framerate_str = video_stream.get('r_frame_rate', '30/1')
            num, den = map(int, original_framerate_str.split('/'))
            original_framerate = num / den
            # Calculate new framerate and clamp it between 10 and original
            new_framerate = max(10, min(original_framerate, original_framerate * compression_ratio))
            output_options['r'] = int(new_framerate)

        elif optimization_type == 'compress_resolution':
            original_height = int(video_stream['height'])
            # Calculate new height, clamp it, and make it even
            new_height = max(240, min(original_height, int(original_height * compression_ratio)))
            if new_height % 2 != 0:
                new_height -= 1  # Ensure height is even
            output_options['vf'] = f'scale=-2:{new_height}' # -2 ensures width is also even

        # Run ffmpeg compression
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
                print(f"Error cleaning up files: {e}")
            return response

        return send_file(output_path, as_attachment=True, download_name=f"compressed_{video.filename}")

    except ffmpeg.Error as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        return f'FFmpeg error:\n{e.stderr.decode()}', 500
    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        return f'An error occurred: {str(e)}', 500

def main():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 80)))

if __name__ == "__main__":
    main()