# CodeSidebar

A lightweight, auto-hiding sidebar application for managing and pasting code snippets quickly.

![CodeSidebar Screenshot](screenshot.jpg)

## Features
- **Auto-Hide & Expand**: Collapses to a thin "vignette" on the edge of your screen when not in use. Simply hover your mouse to expand it instantly.
- **Pin Open**: Toggle the "Pin Open" checkbox to keep the sidebar visible while you work.
- **Categorized Snippets**: Fast access to HTML, JS, and CSS tabs.
- **Custom Snippets**: Add and save your own snippets through a dedicated pop-up window.
- **Persistent Storage**: Custom snippets are saved locally in `snippets.json` and persist between sessions.
- **Search**: Real-time filtering across all snippet categories.
- **Modern UI**: Dark-themed, space-optimized layout designed for developers.

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/DanielZmGt/CodeSidebar.git
cd CodeSidebar
```

### 2. Set up a Virtual Environment (Recommended)
**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Windows
Double-click `Run_CodeSidebar.bat` to launch the app silently in the background.

### macOS/Linux
Run the shell script:
```bash
chmod +x Run_CodeSidebar.sh
./Run_CodeSidebar.sh
```

## License
Distributed under the MIT License. See `LICENSE` for more information.
