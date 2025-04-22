import os
import time
import hashlib
import numpy as np
from PIL import Image, ImageTk, ImageFilter
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad

def log_process(step, data=None):
    """Function to log and print each processing step."""
    if data:
        print(f"\n[PROCESS] {step}: {data}")
    else:
        print(f"\n[PROCESS] {step}")

def refine_image(image_path, output_folder):
    log_process("A. Refining fingerprint image")
    image = Image.open(image_path)
    sharpened_image = image.filter(ImageFilter.SHARPEN)
    refined_path = os.path.join(output_folder, "refined_image.png")
    sharpened_image.save(refined_path)
    log_process("B. Refined image saved", refined_path)
    return refined_path

def preprocess_image(image_path, output_folder):
    log_process("C. Preprocessing fingerprint image")
    image = Image.open(image_path).convert("L")
    threshold = 128
    binarized_image = image.point(lambda p: 255 if p > threshold else 0, '1')
    preprocessed_path = os.path.join(output_folder, "preprocessed.png")
    binarized_image.save(preprocessed_path)
    log_process("D. Preprocessed image saved", preprocessed_path)
    return binarized_image

def generate_feature_matrix(image, output_folder):
    log_process("E. Generating feature matrix")
    image_array = np.array(image)
    feature_matrix = (image_array == 0).astype(int)
    feature_path = os.path.join(output_folder, "feature_matrix.png")
    Image.fromarray((feature_matrix * 255).astype(np.uint8)).save(feature_path)
    log_process("F. Feature matrix saved", feature_path)
    return feature_matrix

def cancellable_transformation(feature_matrix, output_folder):
    log_process("G. Applying cancellable transformation")
    seed = int(time.time() * 1000) % (2**32)
    rng = np.random.default_rng(seed)
    transformed_matrix = rng.permutation(feature_matrix.flatten()).reshape(feature_matrix.shape)
    transformed_path = os.path.join(output_folder, "transformed_matrix.png")
    Image.fromarray((transformed_matrix * 255).astype(np.uint8)).save(transformed_path)
    log_process("H. Transformed feature matrix saved", transformed_path)
    return transformed_matrix

def save_keys(output_folder, C1, C2, C3):
    key_path = os.path.join(output_folder, "cipher_keys.txt")
    with open(key_path, "w") as key_file:
        key_file.write(f"C1: {C1.hex()}\n")
        key_file.write(f"C2: {C2.hex()}\n")
        key_file.write(f"C3: {C3.hex()}\n")
    log_process("I. Cipher keys saved in", key_path)

def save_hash_keys(output_folder, cryptographic_key):
    hash_path = os.path.join(output_folder, "hash_keys.txt")
    binary_code = np.unpackbits(np.frombuffer(cryptographic_key, dtype=np.uint8))[:256]
    with open(hash_path, "w") as hash_file:
        hash_file.write(f"Hash Key: {cryptographic_key.hex()}\n")
        hash_file.write(f"256-bit Binary Key: {''.join(map(str, binary_code))}\n")
    log_process("J. Hash keys saved in", hash_path)

def triple_des_layered_encryption(data, key1, key2, key3, output_folder):
    log_process("K. Starting 3DES encryption with user PIN")
    cipher1 = DES3.new(key1, DES3.MODE_ECB)
    C1 = cipher1.encrypt(pad(data, DES3.block_size))
    log_process("L. C1 (after K1 applied)", C1.hex())
    
    cipher2 = DES3.new(key2, DES3.MODE_ECB)
    C2 = cipher2.encrypt(pad(C1, DES3.block_size))
    log_process("M. C2 (after K2 applied)", C2.hex())
    
    cipher3 = DES3.new(key3, DES3.MODE_ECB)
    C3 = cipher3.encrypt(pad(C2, DES3.block_size))
    log_process("N. C3 (after K3 applied)", C3.hex())
    
    save_keys(output_folder, C1, C2, C3)
    return C3

def generate_cryptographic_key(user_pin, key1, key2, key3, output_folder):
    log_process("O. Generating cryptographic key")
    encrypted_data = triple_des_layered_encryption(user_pin.encode(), key1, key2, key3, output_folder)
    cryptographic_key = hashlib.sha256(encrypted_data).digest()
    log_process("P. Final cryptographic key", cryptographic_key.hex())
    save_hash_keys(output_folder, cryptographic_key)
    return cryptographic_key

def process_fingerprint(image_path, pin, key1, key2, key3):
    log_process("Q. Starting fingerprint processing")
    fingerprint_name = os.path.splitext(os.path.basename(image_path))[0]
    output_folder = os.path.join(os.getcwd(), "3DES", fingerprint_name)
    os.makedirs(output_folder, exist_ok=True)
    refined_image_path = refine_image(image_path, output_folder)
    preprocessed_image = preprocess_image(refined_image_path, output_folder)
    feature_matrix = generate_feature_matrix(preprocessed_image, output_folder)
    transformed_matrix = cancellable_transformation(feature_matrix, output_folder)
    cryptographic_key = generate_cryptographic_key(pin, key1, key2, key3, output_folder)
    log_process("R. Fingerprint processing completed")
    return cryptographic_key

# GUI Setup
root = tk.Tk()
root.title("Cancellable Biometrics with MFA")
root.geometry("600x500")

tk.Label(root, text="Enter Numeric PIN:").pack()
pin_entry = ttk.Entry(root)
pin_entry.pack()

tk.Label(root, text="Enter Key 1:").pack()
key1_entry = ttk.Entry(root)
key1_entry.pack()

tk.Label(root, text="Enter Key 2:").pack()
key2_entry = ttk.Entry(root)
key2_entry.pack()

tk.Label(root, text="Enter Key 3:").pack()
key3_entry = ttk.Entry(root)
key3_entry.pack()

def upload_fingerprint():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
    if not file_path:
        return
    pin = pin_entry.get()
    k1 = key1_entry.get()
    k2 = key2_entry.get()
    k3 = key3_entry.get()
    key1 = hashlib.sha256(k1.encode()).digest()[:24]
    key2 = hashlib.sha256(k2.encode()).digest()[:24]
    key3 = hashlib.sha256(k3.encode()).digest()[:24]
    cryptographic_key = process_fingerprint(file_path, pin, key1, key2, key3)
    hash_label.config(text=f"Generated Hash Key:\n{cryptographic_key.hex()}")
    messagebox.showinfo("Processing Complete", "Fingerprint processing completed successfully!")

upload_button = ttk.Button(root, text="Upload Fingerprint Image", command=upload_fingerprint)
upload_button.pack()
hash_label = tk.Label(root, text="", wraplength=500, justify="center")
hash_label.pack()
root.mainloop()
