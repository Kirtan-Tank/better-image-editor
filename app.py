from PIL import Image, ImageEnhance
import streamlit as st
import numpy as np
import io

st.set_page_config(page_title="White Balance Image Editor", layout="wide")

st.title("🎨 White Balance Image Editor")
st.markdown("Manual image editor inspired by [MinutePhysics](https://youtu.be/WADuXiMZxq4) white balance correction principles.")

# Sidebar: Image upload
st.sidebar.header("Upload Image")
uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)
else:
    st.warning("Please upload an image to begin.")
    st.stop()

# Helper: Apply white balance using gray world algorithm
def gray_world_white_balance(img_array):
    avg_rgb = np.mean(img_array, axis=(0, 1))
    gray_value = np.mean(avg_rgb)
    scale = gray_value / avg_rgb
    balanced = np.clip(img_array * scale, 0, 255).astype(np.uint8)
    return Image.fromarray(balanced)

# Helper: Apply gain
def apply_gain(img_array, red_gain=1.0, blue_gain=1.0):
    balanced = img_array.copy().astype(np.float32)
    balanced[:, :, 0] *= red_gain   # Red channel
    balanced[:, :, 2] *= blue_gain  # Blue channel
    return Image.fromarray(np.clip(balanced, 0, 255).astype(np.uint8))

# Helper: Neutral point white balance
def white_balance_neutral_point(img_array, x, y):
    pixel = img_array[y, x].astype(np.float32)
    gain = np.mean(pixel) / pixel
    corrected = np.clip(img_array * gain, 0, 255).astype(np.uint8)
    return Image.fromarray(corrected)

# Sidebar: Controls
st.sidebar.header("White Balance Settings")
mode = st.sidebar.radio("Correction Mode", ["Manual Gain", "Gray World", "Neutral Point"])

# Gain sliders
red_gain = st.sidebar.slider("Red Gain", 0.5, 2.0, 1.0, 0.01)
blue_gain = st.sidebar.slider("Blue Gain", 0.5, 2.0, 1.0, 0.01)

# Image columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Original Image")
    st.image(image, use_column_width=True)

with col2:
    st.subheader("Edited Image")

    if mode == "Gray World":
        output_image = gray_world_white_balance(img_array)
    elif mode == "Manual Gain":
        output_image = apply_gain(img_array, red_gain, blue_gain)
    else:  # Neutral Point
        st.info("Click on the original image to select a neutral reference point.")
        click = st.image(image, use_column_width=True)
        if "clicked" not in st.session_state:
            st.session_state.clicked = False
        if st.sidebar.button("Simulate Neutral Point Click"):
            # Simulate center pixel for now
            x, y = image.size[0] // 2, image.size[1] // 2
            output_image = white_balance_neutral_point(img_array, x, y)
            st.session_state.clicked = True
        elif st.session_state.clicked:
            x, y = image.size[0] // 2, image.size[1] // 2
            output_image = white_balance_neutral_point(img_array, x, y)
        else:
            output_image = image

    st.image(output_image, use_column_width=True)

# Download section
st.sidebar.header("Export")
img_byte_arr = io.BytesIO()
output_image.save(img_byte_arr, format="PNG")
st.sidebar.download_button(
    label="Download Image",
    data=img_byte_arr.getvalue(),
    file_name="white_balanced.png",
    mime="image/png"
)
