import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile

st.set_page_config(page_title="Image Steganography", layout="centered")
st.title("🔐 Image Steganography Tool")

# ------------------ Helper Functions ------------------

def splitbyte(by):
    return by >> 5, (by >> 2) & 7, by & 3

def merge_bits(bits):
    return (((bits[0] << 3) | bits[1]) << 2) | bits[2]

# ------------------ Embed Message ------------------

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

            img[r, c, 0] |= bits[2]   # Blue
            img[r, c, 1] |= bits[1]   # Green
            img[r, c, 2] |= bits[0]   # Red

            idx += 1
    return img

# ------------------ Extract Message ------------------

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

# ------------------ UI ------------------

option = st.radio("Select Operation", ["Hide Message", "Extract Message"])

uploaded_image = st.file_uploader("📤 Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_image:
    image = Image.open(uploaded_image).convert("RGB")
    img_np = np.array(image)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if option == "Hide Message":
        message = st.text_area("📝 Enter message to hide")

        capacity = img_np.shape[0] * img_np.shape[1] - 1
        st.info(f"📏 Max characters allowed: {capacity}")

        if st.button("🔒 Hide Message"):
            if len(message) == 0:
                st.error("❌ Message cannot be empty.")
            elif len(message) > capacity:
                st.error("❌ Message too long for this image.")
            else:
                stego = embed_message(img_np, message)
                st.image(stego, caption="Stego Image", use_column_width=True)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    cv2.imwrite(tmp.name, cv2.cvtColor(stego, cv2.COLOR_RGB2BGR))
                    st.download_button(
                        "⬇ Download Stego Image",
                        open(tmp.name, "rb"),
                        "stego.png"
                    )

                st.success("✅ Message hidden successfully!")

    else:  # Extract Mode
        if st.button("🔓 Extract Message"):
            try:
                extracted = extract_message(img_np)
                st.success(f"🔑 Hidden Message: {extracted}")
            except:
                st.error("❌ No hidden message found or invalid image.")
