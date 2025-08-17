#Steganography

import cv2 # pip install opencv-python

def spiltbyte(by): #011 000 01
    first_three_bits = by >> 5
    mid_three_bits = (by >> 2) & 7
    last_two_bits = by & 3
    return first_three_bits, mid_three_bits, last_two_bits

def merge_bits(bits) : #[3,0, 1] => 97
    # result = bits[0] <<3 #make room for 3 bits at the RHS
    # result = result | bits[1] #merge the mid 3 bits
    # result = result << 2 #make room for 2 bits at the RHS
    # result = result | bits[2] #merge the mid 2 bits

    return (((bits[0]<<3) | bits[1]) << 2) | bits[2]


def embed(vessel_image, target_image):
    #load the vessel_image into memory
    mem_image = cv2.imread(vessel_image)
    print(type(mem_image))
    print(mem_image.shape)

    #dummy data to embed
    data = [x for x in range(65,91)]
    print(data)
    size = len(data)
    indx = 0

    #embedding loop
    r =0
    while r < mem_image.shape[0] and indx < size:
        c =0
        while c < mem_image.shape[1] and indx < size:
            bits = spiltbyte(data[indx])

            #Free 2,3,3 bits of the pixel
            mem_image[r, c, 0] &= 252  #blue band
            mem_image[r, c, 1] &= 248  #green band
            mem_image[r, c, 2] &= 248  #red band

            #Merge the bits into the bands
            mem_image[r, c, 0] |= bits[2]  # blue band
            mem_image[r, c, 1] |= bits[1]  # green band
            mem_image[r, c, 2] |= bits[0]  # red band

            #next val to embed
            indx+=1

            c+=1
        r+=1

    #save back the image
    cv2.imwrite(target_image, mem_image)

def extract(emb_image):
    #load the image in memory
    mem_img = cv2.imread(emb_image)
    #print(mem_img.shape)
    qty_to_extract = 26
    width = mem_img.shape[1]
    indx =0
    buffer = []
    temp = []
    while indx < qty_to_extract:
        r = indx //width
        c = indx % width
        temp.clear()
        for i in range(3): #0,1,2
            temp.append(mem_img[r,c,2-i] & 2 ** (3 - (i+1) // 3) - 1)

        buffer.append(merge_bits(temp))
        indx+=1


    return buffer

def main():
    embed('D:/Python/Notes/7. Steganography/snake.jpg', 'D:/Python/Notes/7. Steganography/new_snake.png')
    buffer = extract('D:/Python/Notes/7. Steganography/new_snake.png')
    print(buffer)

main()
