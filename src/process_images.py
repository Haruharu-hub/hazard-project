import os
import requests
from PIL import Image
import io
import cairosvg
from urllib.parse import urlparse
from tqdm import tqdm
import hashlib

def resize_and_crop(img, size=(672, 672)):
    # Step 1: Resize while maintaining aspect ratio
    img_ratio = img.width / img.height
    target_ratio = size[0] / size[1]

    if img_ratio > target_ratio:
        # Wider than target
        new_height = size[1]
        new_width = int(new_height * img_ratio)
    else:
        # Taller than target
        new_width = size[0]
        new_height = int(new_width / img_ratio)

    img_resized = img.resize((new_width, new_height), Image.LANCZOS)

    # Step 2: Center crop
    left = (new_width - size[0]) // 2
    top = (new_height - size[1]) // 2
    right = left + size[0]
    bottom = top + size[1]

    img_cropped = img_resized.crop((left, top, right, bottom))

    return img_cropped.convert('RGB') 

def process_all_links(src_root='data/downloaded_images', dst_root = 'data/processed_images'):
    
    os.makedirs(dst_root, exist_ok=True)
    
    valid_extensions = {'.jpg', '.jpeg', '.png'}

    skipped_count = 0
    processed_count = 0

    for dirpath, _, filenames in os.walk(src_root):
        seen_hashes = set()
        for filename in sorted(filenames):
            ext = os.path.splitext(filename)[1].lower()
            if ext in valid_extensions:
                src_path = os.path.join(dirpath, filename)

                relative_path = os.path.relpath(dirpath, src_root)
                dst_dir = os.path.join(dst_root, relative_path)
                os.makedirs(dst_dir, exist_ok=True)
                dst_path = os.path.join(dst_dir, filename)

                try:

                    with open(src_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    if file_hash in seen_hashes:
                        skipped_count += 1
                        print(f"Skipped duplicate: {src_path}")
                        continue  
                    
                    seen_hashes.add(file_hash)

                    with Image.open(src_path) as img:

                        if img.mode == 'P':
                            if 'transparency' in img.info:
                                img = img.convert('RGBA')
                            else:
                                img = img.convert('RGB')

                        if img.mode == 'RGBA':
                            background = Image.new("RGB", img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[3])  
                            img = background

                        processed_img = resize_and_crop(img) 
                        processed_img.save(dst_path)
                        processed_count += 1
                        # print(f"Processed: {src_path} -> {dst_path}")
                except Exception as e:
                    print(f"Failed to process {src_path}: {e}")
            elif filename.startswith('000'):
                src_path = os.path.join(dirpath, filename)
                skipped_count += 1
                print(f"Failed to process format {src_path}")

    print(f"\nTotal processed images: {processed_count}")
    print(f"Total skipped: {skipped_count}")

if __name__ == '__main__':
    process_all_links()


