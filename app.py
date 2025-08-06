import streamlit as st
import numpy as np
from PIL import Image
import cv2

st.set_page_config(page_title="Advanced White Balance Editor", layout="wide")

st.markdown("# 🖼️ Advanced White Balance Editor")
st.markdown(
    "This tool applies white balance correction based on gray-world auto algorithm, manual RB-gain sliders, or custom neutral-point calibration as suggested by MinutePhysics."
)

# Sidebar controls
st.sidebar.header("🎛️ Controls")
# Upload image
uploaded = st.sidebar.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])  
if not uploaded:
    st.sidebar.info("Please upload an image file to begin.")
    st.stop()

# Read image
img = Image.open(uploaded).convert("RGB")
img_np = np.array(img)

# Choose method
method = st.sidebar.radio(
    "Select White Balance Method:",
    ["Gray-World Auto", "Manual RB-Gains", "Custom Neutral Point"]
)

# Function: gray-world
def gray_world_awb(input_img):
    # compute average per channel
    avg_b, avg_g, avg_r = np.mean(input_img[:, :, 0]), np.mean(input_img[:, :, 1]), np.mean(input_img[:, :, 2])
    avg_gray = (avg_b + avg_g + avg_r) / 3

    # scale channels
    scale_b, scale_g, scale_r = avg_gray / avg_b, avg_gray / avg_g, avg_gray / avg_r
    result = np.zeros_like(input_img, dtype=np.float32)
    result[:, :, 0] = np.clip(input_img[:, :, 0] * scale_b, 0, 255)
    result[:, :, 1] = np.clip(input_img[:, :, 1] * scale_g, 0, 255)
    result[:, :, 2] = np.clip(input_img[:, :, 2] * scale_r, 0, 255)
    return result.astype(np.uint8)

# Function: manual RB
def manual_rb_awb(input_img, r_gain, b_gain):
    # convert to float for scaling
    result = input_img.astype(np.float32)
    result[:, :, 2] = np.clip(result[:, :, 2] * r_gain, 0, 255)
    result[:, :, 0] = np.clip(result[:, :, 0] * b_gain, 0, 255)
    return result.astype(np.uint8)

# Function: custom neutral point
def custom_point_awb(input_img, x, y):
    # sample pixel as neutral reference
    neutral = input_img[y, x].astype(np.float32)
    # compute gains so that neutral becomes gray
    avg_neutral = np.mean(neutral)
    gains = avg_neutral / (neutral + 1e-6)
    result = input_img.astype(np.float32) * gains
    return np.clip(result, 0, 255).astype(np.uint8)

# Prepare calibrated image
if method == "Gray-World Auto":
    corrected = gray_world_awb(img_np)
elif method == "Manual RB-Gains":
    st.sidebar.subheader("Adjust Gains")
    r_gain = st.sidebar.slider("Red Channel Gain", 0.5, 2.0, 1.0, 0.01)
    b_gain = st.sidebar.slider("Blue Channel Gain", 0.5, 2.0, 1.0, 0.01)
    corrected = manual_rb_awb(img_np, r_gain, b_gain)
else:
    st.sidebar.subheader("Select Neutral Point")
    st.sidebar.write("Click coordinates in the main image preview.")
    # show clickable image in main area
    coords = st.experimental_get_query_params().get("xy")
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="Original (click to select neutral point)", use_column_width=True, output_format="PNG", clamp=True)
        st.write("Note: After clicking the image, append `?xy=[x]&xy=[y]` in URL and rerun.")
    st.stop()

# Display results
col_orig, col_corr = st.columns(2)
with col_orig:
    st.subheader("Original Image")
    st.image(img_np, use_column_width=True)
with col_corr:
    st.subheader("Corrected Image")
    st.image(corrected, use_column_width=True)

# Download option
result_pil = Image.fromarray(corrected)
buf = st.sidebar.beta_container()
buf.download_button(
    label="📥 Download Corrected Image",
    data=cv2.imencode('.png', corrected)[1].tobytes(),
    file_name='corrected.png',
    mime='image/png'
)  
