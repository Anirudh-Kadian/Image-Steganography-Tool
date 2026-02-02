import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile

st.set_page_config(page_title="Image Steganography", layout="centered")
st.title("🕵️ Image Steganography using OpenCV")

# --- Split a byte into 3,3,2 bits ---
def splitbyte(by):
    return by >> 5, (by >> 2) & 7, by & 3

# --- Merge bits back into byte ---
def merge_bits(bits):
    return (((bits[0] << 3) | bits[1]) << 2) | bits[2]

# --- Embed data ---
def embed(image, data):
    img = image.copy()
    indx = 0

    for r in range(img.shape[0]):
        for c in range(img.shape[1]):
            if indx >= len(data):
                return img

            bits = splitbyte(data[indx])

            img[r, c, 0] &= 252
            img[r, c, 1] &= 248
            img[r, c, 2] &= 248

            img[r, c, 0] |= bits[2]
            img[r, c, 1] |= bits[1]
            img[r, c, 2] |= bits[0]

            indx += 1
    return img

# --- Extract data ---
def extract(img, qty=26):
    width = img.shape[1]
    buffer = []

    for i in range(qty):
        r = i // width
        c = i % width

        bits = [
            img[r, c, 2] & 7,
            img[r, c, 1] & 7,
            img[r, c, 0] & 3
        ]
        buffer.append(merge_bits(bits))

    return buffer

# --- UI ---
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    st.image(image, caption="Original Image", use_column_width=True)

    data = [x for x in range(65, 91)]  # A–Z
    stego_img = embed(img_np, data)

    st.image(stego_img, caption="Stego Image", use_column_width=True)

    extracted = extract(stego_img)
    message = "".join(chr(x) for x in extracted)

    st.success(f"🔓 Extracted Message: {message}")

    # Save for download
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        cv2.imwrite(tmp.name, cv2.cvtColor(stego_img, cv2.COLOR_RGB2BGR))
        st.download_button("⬇ Download Stego Image", open(tmp.name, "rb"), "stego.png")
