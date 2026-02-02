import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile

st.set_page_config(page_title="Image Steganography", layout="centered")
st.title("🔐 Image Steganography Tool")

# --- Helpers ---
def splitbyte(by):
    return by >> 5, (by >> 2) & 7, by & 3

def merge_bits(bits):
    return (((bits[0] << 3) | bits[1]) << 2) | bits[2]

# --- Embed Message ---
def embed_message(image, message):
    data = [len(message)] + [ord(c) for c in message]
    img = image.copy()
    idx = 0

    for r in range(img.shape[0]):
        for c in range(img.shape[1]):
            if idx >= len(data):
                return img

            bits = splitbyte(data[idx])

            img[r, c, 0] &= 252
            img[r, c, 1] &= 248
            img[r, c, 2] &= 248

            img[r, c, 0] |= bits[2]
            img[r, c, 1] |= bits[1]
            img[r, c, 2] |= bits[0]

            idx += 1
    return img

# --- Extract Message ---
def extract_message(image):
    width = image.shape[1]

    # Extract message length
    bits = [
        image[0, 0, 2] & 7,
        image[0, 0, 1] & 7,
        image[0, 0, 0] & 3
    ]
    msg_len = merge_bits(bits)

    chars = []
    for i in range(1, msg_len + 1):
        r = i // width
        c = i % width

        bits = [
            image[r, c, 2] & 7,
            image[r, c, 1] & 7,
            image[r, c, 0] & 3
        ]
        chars.append(chr(merge_bits(bits)))

    return "".join(chars)

# --- UI ---
uploaded_image = st.file_uploader("📤 Upload an image", type=["png", "jpg", "jpeg"])
message = st.text_input("📝 Enter message to hide")

if uploaded_image:
    image = Image.open(uploaded_image).convert("RGB")
    img_np = np.array(image)
    st.image(image, caption="Original Image", use_column_width=True)

    capacity = img_np.shape[0] * img_np.shape[1] - 1

    if st.button("🔒 Hide Message"):
        if len(message) > capacity:
            st.error("❌ Message too long for this image.")
        else:
            stego = embed_message(img_np, message)
            st.image(stego, caption="Stego Image", use_column_width=True)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                cv2.imwrite(tmp.name, cv2.cvtColor(stego, cv2.COLOR_RGB2BGR))
                st.download_button("⬇ Download Stego Image", open(tmp.name, "rb"), "stego.png")

    if st.button("🔓 Extract Message"):
        extracted = extract_message(img_np)
        st.success(f"Hidden Message: {extracted}")
