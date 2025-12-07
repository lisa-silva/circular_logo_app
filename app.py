import streamlit as st
from PIL import Image, ImageDraw, ImageOps
import io

def create_circular_logo_smart(image, output_size=500, fit_mode="fill", bg_color=(255, 255, 255, 0)):
    """
    fit_mode options:
    - "fill": Fill entire circle (may crop edges)
    - "fit": Fit inside circle (may have padding)
    - "stretch": Stretch to fill (distorts aspect ratio)
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Create base image
    base = Image.new('RGBA', (output_size, output_size), bg_color)
    
    # Create circular mask
    mask = Image.new('L', (output_size, output_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([(0, 0), (output_size, output_size)], fill=255)
    
    img_width, img_height = image.size
    
    if fit_mode == "fill":
        # Crop to square then resize (fills circle, crops edges)
        min_dim = min(img_width, img_height)
        left = (img_width - min_dim) // 2
        top = (img_height - min_dim) // 2
        cropped = image.crop((left, top, left + min_dim, top + min_dim))
        resized = cropped.resize((output_size, output_size), Image.Resampling.LANCZOS)
        base.paste(resized, (0, 0), mask)
        
    elif fit_mode == "fit":
        # Resize to fit inside circle (keeps aspect ratio, adds padding)
        scale = min(output_size / img_width, output_size / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        x = (output_size - new_width) // 2
        y = (output_size - new_height) // 2
        base.paste(resized, (x, y), mask)
        
    elif fit_mode == "stretch":
        # Stretch to fill (distorts aspect ratio)
        resized = image.resize((output_size, output_size), Image.Resampling.LANCZOS)
        base.paste(resized, (0, 0), mask)
    
    return base

def main():
    st.title("🔄 Smart Circular Logo Resizer")
    
    uploaded_file = st.file_uploader("Upload logo", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image, caption="Original", use_column_width=True)
        
        with col2:
            # Options
            size = st.slider("Output size:", 100, 1000, 500)
            fit_mode = st.radio("Fit mode:", 
                              ["fill", "fit", "stretch"],
                              format_func=lambda x: {
                                  "fill": "Fill Circle (crop edges)",
                                  "fit": "Fit Inside (add padding)", 
                                  "stretch": "Stretch (distort)"
                              }[x])
            
            bg_color = st.color_picker("Background", "#FFFFFF")
            
            if st.button("Generate"):
                # Convert hex to RGBA
                bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
                bg_rgba = bg_rgb + (255,)
                
                # Create circular logo
                result = create_circular_logo_smart(
                    image, 
                    output_size=size,
                    fit_mode=fit_mode,
                    bg_color=bg_rgba
                )
                
                # Show result
                st.image(result, caption="Result", use_column_width=True)
                
                # Download
                img_bytes = io.BytesIO()
                result.save(img_bytes, format="PNG")
                
                st.download_button(
                    "💾 Download",
                    data=img_bytes.getvalue(),
                    file_name=f"logo_circle_{fit_mode}_{size}x{size}.png",
                    mime="image/png"
                )
