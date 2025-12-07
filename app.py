from PIL import Image, ImageDraw
import math

def create_circular_logo_fixed(image, output_size=500):
    """
    Create circular logo where image fills the entire circle
    """
    # Convert to RGBA if needed
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Calculate scaling to fill circle (no empty edges)
    width, height = image.size
    
    # Get the minimum dimension to make square
    min_dim = min(width, height)
    
    # Crop to square from center
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    
    cropped = image.crop((left, top, right, bottom))
    
    # Resize to output size
    resized = cropped.resize((output_size, output_size), Image.Resampling.LANCZOS)
    
    # Create circular mask
    mask = Image.new('L', (output_size, output_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([(0, 0), (output_size, output_size)], fill=255)
    
    # Apply mask
    result = Image.new('RGBA', (output_size, output_size), (0, 0, 0, 0))
    result.paste(resized, (0, 0), mask)
    
    return result
