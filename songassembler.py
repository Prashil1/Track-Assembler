import csv
import yt_dlp
import subprocess
import os
import re
import shutil

ffmpeg_path = r"C:\Modules\ffmpeg\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe"
files_to_combine = "files_to_combine.txt"
final_files_to_combine = "final_files_to_combine.txt"
list_of_songs = os.path.abspath("list_of_songs.csv")
folder_name = "temp"
youtube_heard_already = {}

def combine_mp3_files_ffmpeg(output_path):
    encoded_already = []
    try:
        # Re-encode each file to ensure consistency (same codec, sample rate, and bit rate)
        with open(files_to_combine, 'r') as file:
            songs = file.readlines()

        # Modify lines based on a condition
        with open(final_files_to_combine, 'a') as final:
            for i, file in enumerate(songs):
                file = file.strip()  # Remove extra whitespace or newline characters

                # Extract the actual file path from the 'file ' wrapper
                if file.startswith("file '") and file.endswith("'"):
                    file_path = file[6:-1]  # Remove the 'file ' prefix and the trailing quote
                
                reencoded_file = f".\{folder_name}/reencoded_{os.path.basename(file_path)}"
                if reencoded_file not in youtube_heard_already:
                    print(f"Re-encoding...{reencoded_file}")

                    command_reencode = [
                    ffmpeg_path, 
                    "-i", file_path,                    # Input file
                    "-c:a", "libmp3lame",           # Set MP3 codec
                    "-b:a", "192k",                 # Set audio bit rate
                    "-ar", "44100",                 # Set sample rate to 44.1kHz
                    "-ac", "2",                     # Force stereo audio
                    reencoded_file                  # Output reencoded file
                    ]
                    subprocess.run(command_reencode, check=True)  # Re-encode the file

                    encoded_already.append(reencoded_file)
                
                # Add to list of Encoded, that we we don't re-encode (transition song).
                final.write(f"file '{reencoded_file}'\n")
        # Use FFmpeg to combine the files
        command = [
            ffmpeg_path, 
            "-f", "concat", 
            "-safe", "0", 
            "-i", final_files_to_combine, 
            "-c", "copy", 
            output_path
        ]
        subprocess.run(command, check=True)

        print(f"MP3 files combined successfully! Output saved at: {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        
def download_youtube_as_mp3(url, output_path='.', start_time=None, end_time=None):  
    # Extract video information using yt-dlp to get the title
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_title = info_dict.get('title', 'unknown_title')

    # Sanitize the filename to remove illegal characters
    video_title = sanitize_filename(video_title)

    # Configuration for yt-dlp to download and extract audio (without postprocessing for mp3)
    ydl_opts = {
        'format': 'bestaudio/best',      # Download the best audio quality
        'extractaudio': True,            # Extract audio only
        'audioquality': 1,               # Set the highest audio quality
        'outtmpl': f'{output_path}/{video_title}.%(ext)s',  # Output filename template
        'noplaylist': True,              # Don't download playlists
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio...")
            ydl.download([url])

        # Get the filename of the downloaded file (assumes .webm format)
        webm_file = f'{output_path}/{video_title}.webm'  # This will be the downloaded format before conversion

        # Convert the downloaded file to MP3 using ffmpeg
        mp3_output = f'{output_path}/{video_title}.mp3'

        youtube_heard_already[url] = mp3_output
        
        print(f"Converting audio to MP3: {mp3_output}...")
        command = [
            ffmpeg_path,               # Full path to ffmpeg executable
            '-i', webm_file,            # Input file (audio)
            '-vn',                      # Disable video
            '-acodec', 'libmp3lame',    # Use MP3 codec
            '-q:a', '0',                # Set audio quality
            mp3_output                  # Output file
        ]
        subprocess.run(command, check=True)

        print(f"MP3 conversion complete! Saved as: {mp3_output}")
        
        # Delete the original .webm file after conversion
        if os.path.exists(webm_file):
            os.remove(webm_file)
            print(f"Deleted the original .webm file: {webm_file}")

        # If trimming is needed
        if start_time is not None and end_time is not None:
            print(f"Trimming MP3 from {start_time}s to {end_time}s...")
            trimmed_mp3 = f"{output_path}/trimmed_{video_title}.mp3"
            return trim_and_fade_audio(mp3_output, trimmed_mp3, start_time, end_time)
        else:
            print(f"Download and conversion complete! MP3 saved as: {mp3_output}")
            return mp3_output

    except Exception as e:
        print(f"Error: {e}")

def trim_and_fade_audio(input_file, output_file, start_time, end_time):
    # Duration for fade-in and fade-out
    fade_duration = 1  # 1 second for fade-in and fade-out
    
    # Run ffmpeg to trim the audio, apply fade-in, and fade-out
    command_trim = [
        ffmpeg_path,               # Full path to ffmpeg executable
        '-i', input_file,          # Input file
        '-ss', str(start_time),    # Start time
        '-to', str(end_time),      # End time
        '-vn',                     # Disable video
        '-acodec', 'libmp3lame',   # MP3 codec
        '-q:a', '0',               # Set audio quality
        #'-af', f'afade=t=in:st=0:d={fade_duration},afade=t=out:st={end_time-fade_duration}:d={fade_duration}',  # Apply fade-in and fade-out
        #'-af', f'afade=t=out:st={end_time-fade_duration}:d={fade_duration}',  # Apply fade-out only
            '-af', f'afade=t=in:st=0:d={fade_duration}',  # Apply fade-in only
        output_file                # Output file
    ]
    
    subprocess.run(command_trim, check=True)

    print(f"Trimmed MP3 with fades saved as: {output_file}")
    return os.path.abspath(output_file)

def sanitize_filename(filename):
    # Define characters that are illegal in filenames (Windows-specific)
    illegal_chars = r'[<>:"/\\|?*]'
    
    # Replace illegal characters with an underscore or just remove them
    sanitized = re.sub(illegal_chars, '_', filename)
    
    # Ensure the filename is not empty
    return sanitized if sanitized else "untitled"

def create_temp_directory():
    try:
        os.mkdir(folder_name)
        print(f"Directory '{folder_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{folder_name}' already exists.")
    except OSError as e:
        print(f"Error creating directory: {e}")

def delete_file_path(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"The file {file_path} has been deleted successfully.")
        except OSError as e:
            print(f"Error deleting file {file_path}: {e}")
    else:
        print(f"The file {file_path} does not exist.")

def is_url(value):
    return re.match(r'http[s]?://', value) is not None

if __name__ == "__main__":
    # Create Temp directory to store songs
    create_temp_directory()

    path_or_link = input("Enter the YouTube video URL for the Transition Song (or leave blank): ").strip()
    transition_song = ""
    if path_or_link:
         start = input("Start time in seconds (or leave blank): ").strip()
         end = input("End time in seconds (or leave blank): ").strip()
         start_time = int(start) if start else 0
         end_time = 1000 if end == -1 else end
         transition_song = download_youtube_as_mp3(path_or_link, output_path=f'.\{folder_name}', start_time=start_time, end_time=end_time)

    # Process csv of songs: YouTube Link/Path, Start Time, End Time
    with open(list_of_songs, 'r') as youtube_list:
        csv_reader = csv.reader(youtube_list)
        with open(files_to_combine, 'a') as file:
            # Write The Transition Song in at the Very Beginning.
            if transition_song != "":
                file.write(f"file '{os.path.abspath(transition_song)}'\n")
            
            # Song Counter
            song_counter = 0
            
            for row in csv_reader:
                song_counter+=1
                # Process if it is a link or a path on disk
                path_or_link, start_time, end_time = row

                if len(row) != 3:
                    print(f"Skipping invalid row: {row}")
                    continue
                try:
                    start_time = int(start_time)  # Start Time
                    end_time = 1000 if int(end_time) == -1 else int(end_time) # End Time
                except ValueError:
                    print(f"Skipping row with invalid integers: {row}")
                    continue

                if is_url(path_or_link):
                    if path_or_link in youtube_heard_already:
                        output_path = os.path.join(folder_name, f"trimmed_song_{song_counter}.mp3")
                        file_to_write = trim_and_fade_audio(youtube_heard_already[path_or_link], output_file=output_path, start_time=start_time, end_time=end_time)
                    else:
                        file_to_write = download_youtube_as_mp3(path_or_link, output_path=f'.\{folder_name}', start_time=start_time, end_time=end_time)
                    # Add Name into master file
                    file.write(f"file '{os.path.abspath(file_to_write)}'\n")

                elif os.path.exists(path_or_link):
                    mp3_file_name = os.path.splitext(os.path.basename(path_or_link))[0]
                    # Use forward slashes or raw strings for paths
                    output_path = os.path.join(folder_name, f"trimmed_Track_{song_counter}_{mp3_file_name}.mp3")

                    file_to_write = trim_and_fade_audio(path_or_link, output_file=output_path, start_time=start_time, end_time=end_time)
                    file.write(f"file '{os.path.abspath(file_to_write)}'\n")

                else:
                    print(f"Path: {path_or_link} (Invalid or non-existent) | Start Time: {start_time} | End Time: {end_time}")
                
                if transition_song != "":
                        file.write(f"file '{os.path.abspath(transition_song)}'\n")
                 
    # Combine All the .mp3 Files
    combine_mp3_files_ffmpeg(r"C:\Track Assembler\Mix 3 v4.mp3")

    # Clean Up.
    delete_file_path(files_to_combine)
    delete_file_path(final_files_to_combine)
    shutil.rmtree(f'.\{folder_name}')