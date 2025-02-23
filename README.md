# Flac Belcher

🤮 Belches FLAC  as separate tracks from the most common cases—supporting files with extensions such as ".flac", ".ape", ".wav", ".alac", and ".tta" in combination with cue sheets, including handling multiple cues and multi-CD releases 

**flac_belcher** is a command-line tool that processes music directories by traversing an input folder, detecting music files and cue sheets, and processing them with ffmpeg. Depending on the file type and the cue data, it either splits multi-track files based on cue sheets or processes individual music files. The tool supports parallel execution and can be deployed in various environments including standalone CLI (tested on Windows and Linux), IDEs, Docker, and via Docker Compose.

---

## Features

- **Cue Sheet Processing:**  
  Splits multi-track audio files based on cue sheets.
  
- **File Type Flexibility:**  
  Handles inconsistencies between cue file references and actual audio file formats (e.g., when a cue references a WAV file, but the actual file is in FLAC, APE, etc.).

- **Parallel Execution:**  
  Uses Python's multiprocessing to execute ffmpeg commands concurrently.

- **Environment Flexibility:**  
  Can be run as a standalone command-line tool, within an IDE, or containerized using Docker and Docker Compose.

---

## Installation

### Prerequisites

- Python 3.12 or later
- ffmpeg (installed on your system or within your container)
- (Optional) Docker and Docker Compose for containerized deployment

Clone the repository:

```bash
git clone https://github.com/vladkar/flac_belcher.git
cd flac_belcher
```

Install the Python dependencies:

```bash
pip install --no-cache-dir -r requirements.txt
```

---

## Usage

### 1. Running via Command Line

After installing the dependencies, you can run the tool from the command line. For example:

```bash
python -m src.main --dir_in /path/to/music/in --dir_out /path/to/music/out --ffmpeg_path ffmpeg
```

This command will process the input directory (`/path/to/music/in`) and place the processed files in the output directory (`/path/to/music/out`).

Additional flags:
- `--dry_run`: Run in dry run mode (commands are printed but not executed).
- `--hide_ffmpeg_logs`: Suppress verbose output from ffmpeg.

### 2. Running via an IDE

1. **Open the Project:**  
   Open the repository folder in your preferred IDE (e.g., VS Code, PyCharm).

2. **Configure Run Settings:**  
   Create a new run configuration with the working directory set to the project root. For example, set the command to:
   ```bash
   python -m src.main --dir_in /path/to/music/in --dir_out /path/to/music/out --ffmpeg_path ffmpeg
   ```
   You can also configure environment variables in your IDE’s run configuration.

3. **Run the Application:**  
   Use your IDE’s run command to start the application.

### 3. Running in Docker

You can build a Docker image for standalone container execution.

**Step 1: Build the Docker Image**

From the project root:

```bash
docker build -t flac_belcher .
```

**Step 2: Run the Docker Container**

```bash
docker run --rm -v /host/path/music_in:/music/in -v /host/path/music_out:/music/out flac_belcher
```

This command mounts your host's music input and output directories into the container and runs the application.

### 4. Running with Docker Compose

If you prefer to use Docker Compose, you can use the provided `docker-compose.yml` file.

**Step 1: Deploy the Stack**

From the project root, run:

```bash
docker-compose up --build
```

This will:
- Build the Docker image from the GitHub repository.
- Create the necessary volumes (ensure your host paths are correctly specified).
- Run the container once (without restarting) using the defined environment variables.

You can customize environment variables in the `docker-compose.yml` file if needed.

---

## Configuration

The application uses several environment variables (or CLI arguments) for configuration:

- **FFMPEG_PATH:**  
  Path to the ffmpeg executable (default: `ffmpeg`). Use .exe file for Win.

- **DIR_IN:**  
  Input directory containing music files (default: `/music/in`).

- **DIR_OUT:**  
  Output directory for processed files (default: `/music/out`).

- **DRY_RUN:**  
  If set to `true`, the application will only print the commands without executing them.

- **HIDE_FFMPEG_LOGS:**  
  If set to `true`, verbose ffmpeg output is suppressed.

These can be provided either via command-line arguments or environment variables.

---

## License

This project is licensed under the [MIT License](LICENSE). Please ensure that attribution is included when using or modifying the software.

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## Contact

For any questions or issues, please open an issue on the GitHub repository or contact the maintainer at vladislav.k.work@gmail.com.
````markdown
