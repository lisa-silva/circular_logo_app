# ============================================
# BLOCK 1: IMPORT TOOLS (Don't change this!)
# ============================================
import streamlit as st
from PIL import Image, ImageDraw
import io

# ============================================
# BLOCK 2: PAGE SETUP (Don't change this!)
# ============================================
st.set_page_config(
    page_title="Circle Logo Maker",
    page_icon="🔄",
    layout="wide"
)

# ============================================
# BLOCK 3: TITLE & INTRO
# ============================================
st.title("🔄 Circle Logo Maker")
st.write("Upload any logo and make it circular in seconds!")

# ============================================
# BLOCK 4: UPLOAD SECTION
# ============================================
uploaded_file = st.file_uploader(
    "📁 Choose your logo file", 
    type=['png', 'jpg', 'jpeg']
)

# ============================================
# BLOCK 5: FUNCTION TO MAKE CIRCLE
# ============================================
def make_circle_logo(image, size=500):
    """Make image circular - MAGIC HAPPENS HERE!"""
    # Make sure image has transparency
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Create square version (crop if needed)
    width, height = image.size
    min_size = min(width, height)
    
    left = (width - min_size) // 2
    top = (height - min_size) // 2
    right = left + min_size
    bottom = top + min_size
    
    square_img = image.crop((left, top, right, bottom))
    
    # Resize to wanted size
    square_img = square_img.resize((size, size), Image.Resampling.LANCZOS)
    
    # Create circle mask (like a cookie cutter!)
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([(0, 0), (size, size)], fill=255)
    
    # Apply mask to image
    result = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    result.paste(square_img, (0, 0), mask)
    
    return result

# ============================================
# BLOCK 6: SHOW PREVIEW & DOWNLOAD
# ============================================
if uploaded_file is not None:
    # Show original image
    original_image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📷 Your Original Logo")
        st.image(original_image, width=300)
        st.caption(f"Size: {original_image.width} × {original_image.height}")
    
    with col2:
        st.subheader("⚙️ Settings")
        
        # Size slider
        logo_size = st.slider(
            "Select logo size:", 
            min_value=100, 
            max_value=1000, 
            value=400, 
            step=50
        )
        
        # Background color
        bg_color = st.color_picker(
            "Choose background color:", 
            "#FFFFFF"
        )
        
        # Generate button
        if st.button("🔄 Make it Circular!", type="primary"):
            with st.spinner("Creating your circle logo..."):
                # Create circular logo
                circle_logo = make_circle_logo(original_image, logo_size)
                
                # Add background color
                if bg_color != "#FFFFFF":
                    # Convert hex to RGB
                    bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
                    background = Image.new('RGB', (logo_size, logo_size), bg_rgb)
                    
                    # Convert circle logo to RGB for background
                    circle_rgb = circle_logo.convert('RGB')
                    background.paste(circle_rgb, (0, 0), circle_logo)
                    circle_logo = background
                
                # Show result
                st.subheader("✅ Your Circle Logo")
                st.image(circle_logo, width=300)
                
                # Create download button
                img_bytes = io.BytesIO()
                
                if bg_color != "#FFFFFF":
                    circle_logo.save(img_bytes, format="PNG")
                else:
                    circle_logo.save(img_bytes, format="PNG")
                
                st.download_button(
                    label="📥 Download PNG",
                    data=img_bytes.getvalue(),
                    file_name="my_circle_logo.png",
                    mime="image/png"
                )
                
                st.success(f"✅ Logo created! Size: {logo_size} × {logo_size} pixels")
                st.balloons()
else:
    st.info("👆 Please upload a logo file to get started!")

# ============================================
# BLOCK 7: FOOTER & INSTRUCTIONS
# ============================================
st.markdown("---")
st.markdown("### 💡 How to use:")
st.markdown("""
1. **Upload** your logo (PNG or JPG)
2. **Choose** your size (slider)
3. **Pick** a background color (optional)
4. **Click** "Make it Circular!"
5. **Download** your new logo!
""")

st.markdown("### 🎯 Perfect for:")
cols = st.columns(4)
with cols[0]:
    st.write("• Social Media")
with cols[1]:
    st.write("• Websites")
with cols[2]:
    st.write("• Business Cards")
with cols[3]:
    st.write("• App Icons")

st.markdown("---")
st.caption("Made with ❤️ using Python + Streamlit")
