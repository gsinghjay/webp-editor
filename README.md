# WebP Image Editor

A modern web application for converting and editing images to WebP format using FastAPI and vanilla JavaScript.

## Features

- 🖼️ Convert various image formats to WebP
- 🎨 Adjust conversion quality settings
- 📱 Responsive design with Bootstrap
- 🖱️ Drag and drop file upload
- 👁️ Live image preview
- 📦 Uses official libwebp tools for optimal conversion

## Prerequisites

- Python 3.8+
- libwebp 1.5.0 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/webp-editor.git
cd webp-editor
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r app/requirements.txt
```

4. Ensure libwebp binaries are available in the `libwebp-1.5.0-linux-aarch64/bin/` directory.

## Usage

1. Start the FastAPI server:
```bash
python app/main.py
```

2. Open your browser and navigate to `http://localhost:8000`

3. Use the web interface to:
   - Drag and drop or select images for conversion
   - Adjust quality settings using the slider
   - Preview images before conversion
   - Download converted WebP files

## Project Structure

```
webp-editor/
├── app/
│   ├── static/
│   │   ├── js/
│   │   ├── css/
│   │   ├── img/
│   │   └── uploads/
│   ├── templates/
│   │   └── index.html
│   ├── main.py
│   └── requirements.txt
├── libwebp-1.5.0-linux-aarch64/
│   └── bin/
│       ├── cwebp
│       ├── dwebp
│       └── ...
└── README.md
```

## API Endpoints

### GET /
- Renders the main application interface
- Returns: HTML page

### POST /upload
- Handles image upload and WebP conversion
- Parameters:
  - `file`: Image file (multipart/form-data)
- Returns: JSON
  ```json
  {
    "success": true,
    "message": "Image converted successfully",
    "webp_path": "/static/uploads/image.webp"
  }
  ```

## Development

### Running Tests
```bash
# TODO: Add test commands
```

### Code Style
This project follows PEP 8 guidelines for Python code. Use a linter to ensure compliance.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [libwebp](https://developers.google.com/speed/webp/docs/api) - WebP compression library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for building APIs
- [Bootstrap](https://getbootstrap.com/) - Frontend framework 