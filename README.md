# WebP Image Editor

A modern web application and API for converting and editing images to WebP format using FastAPI and vanilla JavaScript.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)

## Features

- 🖼️ Convert various image formats to WebP
- 🎨 Multiple resize modes:
  - Exact size
  - Percentage scaling
  - Preset dimensions
  - Fit within dimensions
  - Fill and crop
- 📱 Common platform presets:
  - HD (1280x720)
  - Full HD (1920x1080)
  - QHD (2560x1440)
  - Instagram (1080x1080)
  - Twitter (1200x675)
  - Facebook (1200x630)
  - Thumbnail (150x150)
- 🎯 High-quality WebP conversion with adjustable quality
- 📚 Interactive API documentation (Swagger UI)
- 🖱️ Modern drag-and-drop interface
- 👁️ Live image preview
- 📦 Uses official libwebp tools

## Prerequisites

- Python 3.8+
- libwebp 1.5.0 or higher
- pip (Python package manager)
- Nginx (for production deployment)

## Quick Start

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

4. Run the development server:
```bash
python app/main.py
```

5. Open your browser and navigate to:
   - Web Interface: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Alternative API Docs: `http://localhost:8000/redoc`

## API Documentation

### Endpoints

#### GET /
- Renders the main application interface
- Returns: HTML page

#### POST /edit
- Edit image with various resize options
- Parameters:
  - `file`: Image file (multipart/form-data)
  - `resize_mode`: One of ["exact", "percentage", "preset", "fit", "fill"]
  - `width`: Target width in pixels (for exact, fit, fill modes)
  - `height`: Target height in pixels (for exact, fit, fill modes)
  - `percentage`: Scale percentage 1-200 (for percentage mode)
  - `preset`: Predefined dimensions (for preset mode)
- Returns: JSON
  ```json
  {
    "success": true,
    "message": "Image edited successfully",
    "image_path": "/static/uploads/image.jpg",
    "width": 1920,
    "height": 1080
  }
  ```

#### POST /convert
- Convert image to WebP format
- Parameters:
  - `file`: Image file (multipart/form-data)
  - `quality`: WebP quality 0-100 (default: 75)
- Returns: JSON
  ```json
  {
    "success": true,
    "message": "Image converted successfully",
    "webp_path": "/static/uploads/image.webp",
    "width": 1920,
    "height": 1080
  }
  ```

## Production Deployment

1. Set up Nginx:
```bash
sudo cp deployment/nginx.conf /etc/nginx/sites-available/webp-editor
sudo ln -s /etc/nginx/sites-available/webp-editor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

2. Set up systemd service:
```bash
sudo cp deployment/webp-editor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable webp-editor
sudo systemctl start webp-editor
```

3. Check service status:
```bash
sudo systemctl status webp-editor
```

## Development

### Project Structure
```
webp-editor/
├── app/
│   ├── static/
│   │   ├── uploads/    # Processed images
│   ├── templates/
│   │   └── index.html  # Frontend interface
│   ├── main.py         # FastAPI application
│   └── requirements.txt
├── deployment/
│   ├── nginx.conf
│   ├── webp-editor.service
│   └── deploy.sh
├── .github/
│   └── workflows/
│       └── deploy.yml
└── README.md
```

### Running Tests
```bash
# TODO: Add test commands
```

### Code Style
This project follows:
- PEP 8 for Python code
- Conventional Commits for git commits
- OpenAPI standards for API documentation

## Contributing

1. Fork the repository
2. Create your feature branch:
```bash
git checkout -b feature/amazing-feature
```

3. Commit your changes:
```bash
git commit -m "feat: Add some amazing feature"
```

4. Push to the branch:
```bash
git push origin feature/amazing-feature
```

5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [libwebp](https://developers.google.com/speed/webp/docs/api) - WebP compression library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for building APIs
- [Bootstrap](https://getbootstrap.com/) - Frontend framework 