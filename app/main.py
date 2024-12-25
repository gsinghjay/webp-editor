from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, FileResponse
from fastapi.openapi.utils import get_openapi
import os
import subprocess
from pathlib import Path
import logging
from PIL import Image
from typing import Optional, Literal
from enum import Enum
import time
import shutil
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResizeMode(str, Enum):
    """Available resize modes for image editing."""
    EXACT = "exact"  # Resize to exact dimensions
    PERCENTAGE = "percentage"  # Scale by percentage
    PRESET = "preset"  # Use predefined dimensions
    FIT = "fit"  # Fit within dimensions
    FILL = "fill"  # Fill dimensions and crop

class PresetSize(str, Enum):
    """Predefined image dimensions."""
    HD = "HD"  # 1280x720
    FULL_HD = "FULL_HD"  # 1920x1080
    QHD = "QHD"  # 2560x1440
    INSTAGRAM = "INSTAGRAM"  # 1080x1080
    TWITTER = "TWITTER"  # 1200x675
    FACEBOOK = "FACEBOOK"  # 1200x630
    THUMBNAIL = "THUMBNAIL"  # 150x150

class ImageResponse(BaseModel):
    """Response model for image operations."""
    success: bool
    message: str
    image_path: Optional[str] = None
    webp_path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

PRESET_DIMENSIONS = {
    PresetSize.HD: (1280, 720),
    PresetSize.FULL_HD: (1920, 1080),
    PresetSize.QHD: (2560, 1440),
    PresetSize.INSTAGRAM: (1080, 1080),
    PresetSize.TWITTER: (1200, 675),
    PresetSize.FACEBOOK: (1200, 630),
    PresetSize.THUMBNAIL: (150, 150)
}

app = FastAPI(
    title="WebP Image Editor API",
    description="""
    A modern API for image editing and WebP conversion.
    
    Features:
    * Image resizing with multiple modes
    * Preset dimensions for common platforms
    * High-quality WebP conversion
    * Detailed operation feedback
    """,
    version="1.0.0",
    contact={
        "name": "WebP Editor Team",
        "url": "https://github.com/yourusername/webp-editor",
    },
    license_info={
        "name": "MIT",
    }
)

# Mount static files
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="/app/templates")

# Ensure upload directory exists
UPLOAD_DIR = Path("/app/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def resize_image(img: Image.Image, resize_mode: ResizeMode, width: Optional[int] = None, 
                height: Optional[int] = None, percentage: Optional[int] = None,
                preset: Optional[PresetSize] = None) -> Image.Image:
    """Resize image based on the specified mode and parameters."""
    
    original_width, original_height = img.size
    
    if resize_mode == ResizeMode.EXACT:
        if not width or not height:
            raise ValueError("Width and height required for exact resize mode")
        return img.resize((width, height), Image.Resampling.LANCZOS)
    
    elif resize_mode == ResizeMode.PERCENTAGE:
        if not percentage:
            raise ValueError("Percentage required for percentage resize mode")
        new_width = int(original_width * percentage / 100)
        new_height = int(original_height * percentage / 100)
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    elif resize_mode == ResizeMode.PRESET:
        if not preset:
            raise ValueError("Preset required for preset resize mode")
        target_width, target_height = PRESET_DIMENSIONS[preset]
        return img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    elif resize_mode == ResizeMode.FIT:
        if not width or not height:
            raise ValueError("Width and height required for fit resize mode")
        img.thumbnail((width, height), Image.Resampling.LANCZOS)
        return img
    
    elif resize_mode == ResizeMode.FILL:
        if not width or not height:
            raise ValueError("Width and height required for fill resize mode")
        
        # Calculate target ratio and current ratio
        target_ratio = width / height
        current_ratio = original_width / original_height
        
        if current_ratio > target_ratio:
            # Image is wider than target
            new_height = height
            new_width = int(height * current_ratio)
        else:
            # Image is taller than target
            new_width = width
            new_height = int(width / current_ratio)
        
        # Resize to cover the target dimensions
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Calculate crop box
        left = (new_width - width) // 2
        top = (new_height - height) // 2
        right = left + width
        bottom = top + height
        
        # Crop to exact dimensions
        return img.crop((left, top, right, bottom))
    
    raise ValueError(f"Unsupported resize mode: {resize_mode}")

@app.get("/", tags=["Frontend"])
async def home(request: Request):
    """
    Render the web interface for the image editor.
    
    Returns:
        HTML: The main application interface
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/edit", 
         response_model=ImageResponse,
         tags=["Image Operations"],
         summary="Edit an image",
         response_description="Returns the edited image information")
async def edit_image(
    file: UploadFile = File(..., description="The image file to edit"),
    resize_mode: Optional[ResizeMode] = Form(None, description="The resize mode to apply"),
    width: Optional[int] = Form(None, description="Target width in pixels", gt=0),
    height: Optional[int] = Form(None, description="Target height in pixels", gt=0),
    percentage: Optional[int] = Form(None, description="Scale percentage (1-200)", ge=1, le=200),
    preset: Optional[PresetSize] = Form(None, description="Predefined image dimensions")
):
    """
    Edit an uploaded image with various resize options.

    - **file**: The image file to edit (supports common formats: JPG, PNG, etc.)
    - **resize_mode**: How to resize the image
        - exact: Resize to exact dimensions
        - percentage: Scale by percentage
        - preset: Use predefined dimensions
        - fit: Fit within dimensions
        - fill: Fill dimensions and crop
    - **width**: Target width (required for exact, fit, fill modes)
    - **height**: Target height (required for exact, fit, fill modes)
    - **percentage**: Scale percentage (required for percentage mode)
    - **preset**: Predefined dimensions (required for preset mode)

    Returns:
        ImageResponse: Information about the edited image
    """
    file_path = None
    
    try:
        logger.info(f"Received file for editing: {file.filename}")
        logger.info(f"Resize params - mode: {resize_mode}, width: {width}, height: {height}, "
                   f"percentage: {percentage}, preset: {preset}")
        
        # Generate a unique filename
        timestamp = int(time.time() * 1000)
        safe_filename = f"image_{timestamp}"
        
        # Save original file with original extension
        original_ext = os.path.splitext(file.filename)[1] or '.jpg'
        file_path = UPLOAD_DIR / f"{safe_filename}{original_ext}"
        
        logger.info(f"Saving file to: {file_path}")
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Resize image if requested
        if resize_mode:
            try:
                with Image.open(file_path) as img:
                    logger.info(f"Original image size: {img.size}")
                    resized_img = resize_image(
                        img=img,
                        resize_mode=resize_mode,
                        width=width,
                        height=height,
                        percentage=percentage,
                        preset=preset
                    )
                    resized_img.save(file_path)
                    final_width, final_height = resized_img.size
                    logger.info(f"Resized image to {resized_img.size}")
            except Exception as e:
                logger.error(f"Resize error: {str(e)}")
                raise ValueError(f"Resize failed: {str(e)}")
        else:
            with Image.open(file_path) as img:
                final_width, final_height = img.size

        # Construct the correct static URL path
        static_path = f"/static/uploads/{file_path.name}"
        logger.info(f"Generated static path: {static_path}")
        
        return JSONResponse({
            "success": True,
            "message": "Image edited successfully",
            "image_path": static_path,
            "width": final_width,
            "height": final_height
        })
            
    except Exception as e:
        logger.exception("Error during image editing")
        if file_path and file_path.exists():
            file_path.unlink()
        return JSONResponse({
            "success": False,
            "message": str(e)
        }, status_code=500)

@app.post("/convert",
          response_model=ImageResponse,
          tags=["Image Operations"],
          summary="Convert image to WebP",
          response_description="Returns the converted WebP image information")
async def convert_to_webp(
    file: UploadFile = File(..., description="The image file to convert"),
    quality: int = Form(75, description="WebP quality (0-100)", ge=0, le=100)
):
    """
    Convert an uploaded image to WebP format.

    - **file**: The image file to convert (supports common formats: JPG, PNG, etc.)
    - **quality**: WebP quality setting
        - Range: 0-100
        - Higher values = better quality but larger file size
        - Default: 75

    Returns:
        ImageResponse: Information about the converted WebP image
    """
    file_path = None
    output_path = None
    
    try:
        logger.info(f"Received file for WebP conversion: {file.filename}")
        logger.info(f"Quality: {quality}")
        
        # Validate quality parameter
        quality = max(0, min(100, quality))
        
        # Generate a unique filename
        timestamp = int(time.time() * 1000)
        safe_filename = f"image_{timestamp}"
        
        # Save original file
        original_ext = os.path.splitext(file.filename)[1] or '.jpg'
        file_path = UPLOAD_DIR / f"{safe_filename}{original_ext}"
        output_path = UPLOAD_DIR / f"{safe_filename}.webp"
        
        logger.info(f"Saving file to: {file_path}")
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Convert to WebP using cwebp
        cwebp_path = "cwebp"  # Use system installed cwebp
        
        # Build command with quality parameter
        command = [
            cwebp_path,
            "-q", str(quality),
            str(file_path),
            "-o", str(output_path)
        ]
        
        logger.info(f"Running conversion command: {' '.join(command)}")
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )
        
        # Log the command output
        logger.info(f"Command stdout: {result.stdout}")
        if result.stderr:
            logger.error(f"Command stderr: {result.stderr}")
        
        if result.returncode == 0:
            # Get final image dimensions
            with Image.open(output_path) as img:
                final_width, final_height = img.size
                logger.info(f"Final image dimensions: {final_width}x{final_height}")

            # Clean up original file
            if file_path and file_path.exists():
                file_path.unlink()
            
            # Construct the correct static URL path
            static_path = f"/static/uploads/{output_path.name}"
            logger.info(f"Generated static path: {static_path}")
            
            return JSONResponse({
                "success": True,
                "message": "Image converted to WebP successfully",
                "webp_path": static_path,
                "width": final_width,
                "height": final_height
            })
        else:
            raise ValueError(f"Conversion failed: {result.stderr}")
            
    except Exception as e:
        logger.exception("Error during WebP conversion")
        # Clean up files on error
        if file_path and file_path.exists():
            file_path.unlink()
        if output_path and output_path.exists():
            output_path.unlink()
            
        return JSONResponse({
            "success": False,
            "message": str(e)
        }, status_code=500)

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {"status": "healthy"}

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    """Serve favicon"""
    return FileResponse(os.path.join('/app/static/img', 'favicon.ico'))

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add API logo/favicon
    openapi_schema["info"]["x-logo"] = {
        "url": "https://developers.google.com/speed/webp/images/webp-logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
