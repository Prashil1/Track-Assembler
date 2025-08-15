🛠️ Installation

Before running the project, you need to install the required dependencies.

1. Install FFmpeg

This project requires FFmpeg for audio processing. Download and install FFmpeg from the official website:

👉 [FFmpeg Download](https://ffmpeg.org/download.html)

Once installed, make sure to specify the path to the FFmpeg executable in your code using the ffmpeg_path variable.

2. Install Python Dependencies

This project uses the yt_dlp library to download and handle YouTube videos (and other media). You can install the required Python package using pip:

pip install yt-dlp

3. Set ffmpeg_path

In your code, define the path to where FFmpeg is installed. For example:

ffmpeg_path = "/path/to/ffmpeg"  # Change this to the actual path on your system in the [songassembler.py](https://github.com/Prashil1/Track-Assembler/blob/main/songassembler.py) file


📖 Usage

This project supports transition music playback, using a provided list of songs with optional time ranges.

🎵 Song List Format

To specify which songs to use, create a CSV file named list_of_songs.csv. Each row in the file should contain:

<song_link_or_path>,<start_time>,<end_time>


song_link_or_path: Either a local path to an .mp3 file, or a link to a streaming source (e.g., a YouTube URL).

start_time: The start time (in seconds) for playback. Use 0 to start from the beginning.

end_time: The end time (in seconds) for playback. Use -1 to play to the end of the song.

📂 Example ([list_of_songs.csv](https://github.com/Prashil1/Track-Assembler/blob/main/list_of_songs.csv))
https://www.youtube.com/watch?v=dQw4w9WgXcQ,0,-1
/path/to/local/song.mp3,15,45