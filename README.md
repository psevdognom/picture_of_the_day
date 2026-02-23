# Wikipedia Photo of the Day → Zoom background

Downloads previous "Picture of the Day" images from Ukrainian Wikipedia and cycles through them as Zoom backgrounds, changing every 5 minutes.

## Features
- Fetches historical "Picture of the Day" images from Ukrainian Wikipedia archives
- Cycles through the last 30 days of featured pictures
- Changes the background every 5 minutes
- Copies the current image to Zoom's `VirtualBkgnd_Custom` folder

## Files
\- `main.py` — script that downloads historical POTD images and copies them to the Zoom folder.  
\- `jobs.yaml` — example `cronn` job config (runs every 5 minutes).  
\- `requirements.txt` — Python dependencies.  
\- `README.md` — this file.

## Requirements
\- macOS  
\- Python 3.8+  
\- pip

## Install Python deps
```bash
pip install -r requirements.txt
```

