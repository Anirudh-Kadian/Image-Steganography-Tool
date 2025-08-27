# Steganography with OpenCV (Google Colab Ready)

import cv2
from google.colab import files

# --- Split a byte into 3,3,2 bits ---
def spiltbyte(by):
    first_three_bits = by >> 5
    mid_three_bits = (by >> 2) & 7
    last_two_bits = by & 3
    return first_three_bits, mid_three_bits, last_two_bits

# --- Merge 3,3,2 bits back into one byte ---
def merge_bits(bits):
    return (((bits[0] << 3) | bits[1]) << 2) | bits[2]

# --- Embed hidden data inside an image ---
def embed(vessel_image, target_image):
    mem_image = cv2.imread(vessel_image)
    if mem_image is None:
        raise FileNotFoundError("Image not found. Make sure you uploaded it!")

    # Dummy data to embed: ASCII values A–Z
    data = [x for x in range(65, 91)]
    print("Data to embed:", [chr(x) for x in data])

    size = len(data)
    indx = 0

    r = 0
    while r < mem_image.shape[0] and indx < size:
        c = 0
        while c < mem_image.shape[1] and indx < size:
            bits = spiltbyte(data[indx])

            # Clear 2,3,3 bits of pixel
            mem_image[r, c, 0] &= 252  # blue (keep 6 MSBs)
            mem_image[r, c, 1] &= 248  # green (keep 5 MSBs)
            mem_image[r, c, 2] &= 248  # red (keep 5 MSBs)

            # Embed bits
            mem_image[r, c, 0] |= bits[2]  # blue → 2 bits
            mem_image[r, c, 1] |= bits[1]  # green → 3 bits
            mem_image[r, c, 2] |= bits[0]  # red → 3 bits

            indx += 1
            c += 1
        r += 1

    cv2.imwrite(target_image, mem_image)

# --- Extract hidden data from image ---
def extract(emb_image):
    mem_img = cv2.imread(emb_image)
    if mem_img is None:
        raise FileNotFoundError("Embedded image not found!")

    qty_to_extract = 26  # number of characters embedded (A–Z)
    width = mem_img.shape[1]
    indx = 0
    buffer = []

    while indx < qty_to_extract:
        r = indx // width
        c = indx % width

        # Extract 3,3,2 bits (reverse of embed)
        temp = [
            mem_img[r, c, 2] & 7,  # red (3 bits)
            mem_img[r, c, 1] & 7,  # green (3 bits)
            mem_img[r, c, 0] & 3   # blue (2 bits)
        ]

        buffer.append(merge_bits(temp))
        indx += 1

    return buffer

# --- Main ---
def main():
    # Upload cover image
    uploaded = files.upload()
    vessel_image = list(uploaded.keys())[0]

    # Embed data
    embed(vessel_image, "new_snake.png")

    # Extract data
    buffer = extract("new_snake.png")
    print("Extracted ASCII values:", buffer)
    print("Extracted message:", "".join([chr(x) for x in buffer]))

    # Download the stego image
    files.download("new_snake.png")

main()
