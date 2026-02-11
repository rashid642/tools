from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import os
import subprocess
import shutil

async def execute(request: Request):
    """
    Extract audio from video file using FFmpeg
    
    Expected form data:
    - file: Video file (MP4, AVI, MOV, MKV, WebM, etc.)
    - format: Output audio format (mp3, wav, aac, ogg, flac)
    - quality: Audio quality/bitrate (optional)
    """
    temp_input = None
    temp_output = None
    
    try:
        print(f"[Video to Audio] Processing request")
        
        # Get form data
        form = await request.form()
        video_file = form.get('file')
        output_format = form.get('format', 'mp3').lower()
        quality = form.get('quality', 'high')
        
        if not video_file:
            return JSONResponse(
                {"error": "No video file provided"},
                status_code=400
            )
        
        # Validate output format
        valid_formats = ['mp3', 'wav', 'aac', 'ogg', 'flac', 'm4a']
        if output_format not in valid_formats:
            return JSONResponse(
                {"error": f"Invalid format. Supported: {', '.join(valid_formats)}"},
                status_code=400
            )
        
        # Read video file
        video_content = await video_file.read()
        print(f"[Video to Audio] Received video: {video_file.filename}, size: {len(video_content)} bytes")
        
        # Create temporary files
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video_file.filename)[1])
        temp_input.write(video_content)
        temp_input.close()
        
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format}')
        temp_output.close()
        
        # Determine FFmpeg audio quality settings
        audio_params = []
        if output_format == 'mp3':
            if quality == 'high':
                audio_params = ['-b:a', '320k']
            elif quality == 'medium':
                audio_params = ['-b:a', '192k']
            else:  # low
                audio_params = ['-b:a', '128k']
        elif output_format == 'aac' or output_format == 'm4a':
            if quality == 'high':
                audio_params = ['-b:a', '256k']
            elif quality == 'medium':
                audio_params = ['-b:a', '128k']
            else:  # low
                audio_params = ['-b:a', '96k']
        elif output_format == 'ogg':
            if quality == 'high':
                audio_params = ['-q:a', '8']
            elif quality == 'medium':
                audio_params = ['-q:a', '5']
            else:  # low
                audio_params = ['-q:a', '3']
        # WAV and FLAC use default settings (lossless)
        
        # Build FFmpeg command
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', temp_input.name,
            '-vn',  # No video
            '-acodec', 'libmp3lame' if output_format == 'mp3' else 
                       'aac' if output_format in ['aac', 'm4a'] else
                       'libvorbis' if output_format == 'ogg' else
                       'flac' if output_format == 'flac' else
                       'pcm_s16le',  # WAV
            *audio_params,
            '-y',  # Overwrite output file
            temp_output.name
        ]
        
        print(f"[Video to Audio] Running FFmpeg: {' '.join(ffmpeg_cmd)}")
        
        # Run FFmpeg
        result = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8')
            print(f"[Video to Audio] FFmpeg error: {error_msg}")
            return JSONResponse(
                {"error": f"Audio extraction failed: {error_msg[:200]}"},
                status_code=500
            )
        
        # Check if output file exists and has content
        if not os.path.exists(temp_output.name) or os.path.getsize(temp_output.name) == 0:
            return JSONResponse(
                {"error": "Audio extraction failed: Output file is empty"},
                status_code=500
            )
        
        output_size = os.path.getsize(temp_output.name)
        print(f"[Video to Audio] Success: Extracted audio to {output_format}, size: {output_size} bytes")
        
        # Generate output filename
        base_name = os.path.splitext(video_file.filename)[0]
        output_filename = f"{base_name}.{output_format}"
        
        # Return the audio file
        return FileResponse(
            temp_output.name,
            media_type=f'audio/{output_format}',
            filename=output_filename,
            background=lambda: cleanup_files(temp_input.name, temp_output.name)
        )
        
    except subprocess.TimeoutExpired:
        print(f"[Video to Audio] Error: FFmpeg timeout")
        cleanup_files(temp_input.name if temp_input else None, temp_output.name if temp_output else None)
        return JSONResponse(
            {"error": "Processing timeout. Video file may be too large."},
            status_code=500
        )
    except Exception as e:
        print(f"[Video to Audio] Error: {e}")
        import traceback
        traceback.print_exc()
        cleanup_files(temp_input.name if temp_input else None, temp_output.name if temp_output else None)
        return JSONResponse(
            {"error": f"Error: {str(e)}"},
            status_code=500
        )

def cleanup_files(*file_paths):
    """Clean up temporary files"""
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.unlink(path)
                print(f"[Video to Audio] Cleaned up: {path}")
            except Exception as e:
                print(f"[Video to Audio] Error cleaning up file {path}: {e}")

