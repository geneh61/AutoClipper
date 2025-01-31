# Auto Video Clipper

Python script that splits videos into clips based on a volume threshold.

## Requirements
- Python 3.6+
- FFmpeg installed and accessible in PATH
- Required Python packages

## Installation

1. Clone repo:
```bash
git clone https://github.com/geneh61/AutoClipper.git
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Ensure FFmpeg is installed and accessible in your system PATH:

FFmpeg: https://www.ffmpeg.org/download.html

## Usage
1. Run the script:
```bash
python video_splitter.py
```
2. Select your video file using the "Browse" button
3. Choose an output folder
4. Adjust settings:
   - Volume threshold (or use auto-detect)
   - Minimum segment length
   - Maximum segment length
5. Click "Start Processing"
6. Wait for processing to complete
7. Access your clips in the output folder

## License
MIT License - See LICENSE file for details
