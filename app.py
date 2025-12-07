import streamlit as st
from PIL import Image, ImageDraw
import io
import numpy as np

st.set_page_config(page_title="Perfect Circle Logo", layout="wide")

st.title("🎯 Perfect Circular Logo Maker")
st.markdown("Transform any logo into a perfect circle with proper scaling")

# Upload
uploaded_file = st.file_uploader("Choose a logo image", type=['png', 'jpg', 'jpeg', 'gif'])

if uploaded_file:
    original = Image.open(uploaded_file).convert("RGBA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Logo")
        st.image(original, use_column_width=True)
        
        # Show original dimensions
        w, h = original.size
        st.caption(f"Original size: {w} × {h} pixels")
    
    with col2:
        st.subheader("Customization")
        
        # Size
        output_size = st.slider("Output size (pixels):", 100, 1000, 500)
        
        # Fit options
        fit_option = st.selectbox(
            "How should the image fit?",
            [
                "fill_circle", 
                "fit_inside", 
                "crop_to_circle"
            ],
            format_func=lambda x: {
                "fill_circle": "Fill Circle (crop edges if needed)",
                "fit_inside": "Fit Inside Circle (add padding)",
                "crop_to_circle": "Crop to Circle (exact circle from center)"
            }[x]
        )
        
        # Background
        use_bg = st.checkbox("Add background color", value=True)
        bg_color = "#FFFFFF"
        if use_bg:
            bg_color = st.color_picker("Choose background color", "#FFFFFF")
        
        # Border
        add_border = st.checkbox("Add border", value=False)
        border_color = "#000000"
        border_width = 5
        if add_border:
            border_color = st.color_picker("Border color", "#000000")
            border_width = st.slider("Border width", 1, 20, 5)
        
        # Generate button
        if st.button("🔄 Create Circular Logo", type="primary"):
            with st.spinner("Creating perfect circular logo..."):
                # Create the circular logo
                result = create_perfect_circular_logo(
                    original,
                    size=output_size,
                    fit_mode=fit_option,
                    bg_color=bg_color,
                    border_color=border_color if add_border else None,
                    border_width=border_width if add_border else 0
                )
                
                # Show result
                st.subheader("Result")
                st.image(result, use_column_width=True)
                
                # Create download
                img_bytes = io.BytesIO()
                result.save(img_bytes, format="PNG", optimize=True)
                
                # Download button
                st.download_button(
                    label="📥 Download PNG",
                    data=img_bytes.getvalue(),
                    file_name=f"perfect_circular_logo_{output_size}px.png",
                    mime="image/png",
                    use_container_width=True
                )
                
                st.success(f"✅ Perfect circular logo created at {output_size}×{output_size} pixels!")

def create_perfect_circular_logo(image, size=500, fit_mode="fill_circle", 
                                bg_color="#FFFFFF", border_color=None, border_width=0):
    """
    Creates a perfect circular logo with proper image scaling
    """
    # Convert hex color to RGB/RGBA
    def hex_to_rgba(hex_color, alpha=255):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return rgb + (alpha,)
    
    bg_rgba = hex_to_rgba(bg_color)
    
    # Create base image with background
    base = Image.new('RGBA', (size, size), bg_rgba)
    
    # Create circular mask
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([(0, 0), (size, size)], fill=255)
    
    img_w, img_h = image.size
    
    if fit_mode == "fill_circle":
        # Fill entire circle (crop to square, then resize)
        min_dim = min(img_w, img_h)
        left = (img_w - min_dim) // 2
        top = (img_h - min_dim) // 2
        cropped = image.crop((left, top, left + min_dim, top + min_dim))
        
        # Resize to output size
        resized = cropped.resize((size, size), Image.Resampling.LANCZOS)
        
        # Apply circular mask
        temp = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        temp.paste(resized, (0, 0), mask)
        base = Image.alpha_composite(base, temp)
    
    elif fit_mode == "fit_inside":
        # Fit inside circle (resize maintaining aspect ratio)
        scale = min(size / img_w, size / img_h) * 0.9  # 90% to add padding
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        
        resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Center the image
        x = (size - new_w) // 2
        y = (size - new_h) // 2
        
        temp = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        temp.paste(resized, (x, y), mask)
        base = Image.alpha_composite(base, temp)
    
    elif fit_mode == "crop_to_circle":
        # Crop a circular area from center of original
        # Create mask at original size
        original_mask = Image.new('L', (img_w, img_h), 0)
        original_draw = ImageDraw.Draw(original_mask)
        
        # Create circle in center of original
        circle_diameter = min(img_w, img_h)
        left = (img_w - circle_diameter) // 2
        top = (img_h - circle_diameter) // 2
        original_draw.ellipse([(left, top), (left + circle_diameter, top + circle_diameter)], fill=255)
        
        # Apply mask to original
        temp = Image.new('RGBA', (img_w, img_h), (0, 0, 0, 0))
        temp.paste(image, (0, 0), original_mask)
        
        # Crop to the circle bounds
        cropped = temp.crop((left, top, left + circle_diameter, top + circle_diameter))
        
        # Resize to output size
        resized = cropped.resize((size, size), Image.Resampling.LANCZOS)
        base.paste(resized, (0, 0), resized)
    
    # Add border if requested
    if border_color and border_width > 0:
        border_rgba = hex_to_rgba(border_color)
        border_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        border_draw = ImageDraw.Draw(border_img)
        
        # Draw border
        border_draw.ellipse(
            [(border_width//2, border_width//2), 
             (size - border_width//2, size - border_width//2)],
            outline=border_rgba,
            width=border_width
        )
        
        base = Image.alpha_composite(base, border_img)
    
    return base

# Add info section
st.markdown("---")
st.markdown("### 📊 Fit Mode Explanation:")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    **Fill Circle** 
    - Crops image to square
    - Resizes to fill circle
    - No empty space
    """)
    
with col2:
    st.markdown("""
    **Fit Inside**
    - Keeps full image
    - Adds padding if needed
    - Maintains aspect ratio
    """)
    
with col3:
    st.markdown("""
    **Crop to Circle**
    - Takes circular area from center
    - Preserves original quality
    - No distortion
    """)

st.markdown("""
<div style='text-align: center; margin-top: 30px; color: #666;'>
    <p>Your downloaded logo will now have the image properly sized inside the circle! ✅</p>
</div>
""", unsafe_allow_html=True)
