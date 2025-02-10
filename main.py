import numpy as np
import cv2
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
 
def encrypt(raw, key):
    private_key = hashlib.sha256(key.encode("utf-8")).digest()
    raw = str.encode(pad(raw))
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw))
 
 
def decrypt(enc, key):
    private_key = hashlib.sha256(key.encode("utf-8")).digest()
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:]))

def msgtobinary(msg):
    if type(msg) == str:
        result= ''.join([ format(ord(i), "08b") for i in msg ])
    
    elif type(msg) == bytes or type(msg) == np.ndarray:
        result= [ format(i, "08b") for i in msg ]
    
    elif type(msg) == int or type(msg) == np.uint8:
        result=format(msg, "08b")

    else:
        raise TypeError("Input type is not supported in this function")
    
    return result

def encode_img_data(img):
    data=input("\nEnter the data to be Encoded in Image: ")    
    if (len(data) == 0): 
        raise ValueError('Data entered to be encoded is empty')
  
    nameoffile = input("\nEnter the name of the New Image (Stego Image) after Encoding (with .png extension): ")
    
    no_of_bytes=(img.shape[0] * img.shape[1] * 3) // 8
    
    print("\t\nMaximum bytes to encode in Image: ", no_of_bytes)
    
    encr_key = input("Enter a key for AES encryption: ") # key for encryption
    encrypted_data = encrypt(data, encr_key) # encryption of data
    
    stego_key = input("\nEnter a key to encode the data: ")
    
    data = stego_key + bytes.decode(encrypted_data) # combining the keys and encrypted data
    
    if(len(data)>no_of_bytes):
        raise ValueError("Insufficient bytes Error, Need Bigger Image or give Less Data !!")
    
    data +='*^*^*'    
    
    binary_data=msgtobinary(data)
    print("\n")
    length_data=len(binary_data)
    
    print("\nThe Length of Binary data: ",length_data)
    
    index_data = 0
    
    for i in img:
        for pixel in i:
            r, g, b = msgtobinary(pixel)
            if index_data < length_data:
                pixel[0] = int(r[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[1] = int(g[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[2] = int(b[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data >= length_data:
                break
    cv2.imwrite(nameoffile,img)
    print("\nEncoded the data successfully in the Image and the image is successfully saved with name: ",nameoffile)

def decode_img_data(img):
    stego_key = input("\nEnter the key to decode the data: ") # key for decoding
    decr_key = input("Enter the key for AES decryption: ") # key for decryption
    
    data_binary = ""
    for i in img:
        for pixel in i:
            r, g, b = msgtobinary(pixel) 
            data_binary += r[-1]  
            data_binary += g[-1]  
            data_binary += b[-1]  
            total_bytes = [ data_binary[i: i+8] for i in range(0, len(data_binary), 8) ]
            decoded_data = ""
            for byte in total_bytes:
                decoded_data += chr(int(byte, 2))
                if decoded_data[-5:] == "*^*^*": 
                    if decoded_data[:len(stego_key)] == stego_key:
                        decrypted = bytes.decode(decrypt(str.encode(decoded_data[len(stego_key):-5]), decr_key)) # decryption of data
                        print("\n\nThe Encoded data which was hidden in the Image was: ", decrypted)
                        return
                    else:
                        print("\n\nThe key entered is incorrect")
                        return
    return
                 
def main():
    print("\t\t      STEGANOGRAPHY")   
    while True:
        print("\n\t\tIMAGE STEGANOGRAPHY OPERATIONS\n") 
        print("1. Encode the Text message") 
        print("2. Decode the Text message") 
        print("3. Exit")  
        choice1 = int(input("Enter the Choice: "))   
        if choice1 == 1:
            try:
                image_path = input("Enter the Image you need to encode to hide the Secret message: ")
                image = cv2.imread(image_path)
                if image is None:
                    raise FileNotFoundError("Error: The specified image file was not found or could not be loaded.")
                encode_img_data(image)
            except FileNotFoundError as e:
                print(e)
        elif choice1 == 2:
            try:
                image_path = input("Enter the Image you need to decode to get the Secret message: ")
                image1 = cv2.imread(image_path)
                if image1 is None:
                    raise FileNotFoundError("Error: The specified image file was not found or could not be loaded.")
                decode_img_data(image1)
            except FileNotFoundError as e:
                print(e)
        elif choice1 == 3:
            break
        else:
            print("Incorrect Choice")
        print("\n")

if __name__ == "__main__":
    main()
