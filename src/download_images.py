import os
import requests
from PIL import Image
import io
import cairosvg
from urllib.parse import urlparse
from tqdm import tqdm

def get_extension_and_format(url, content_type):

    if 'image/jpeg' in content_type:
        return '.jpg', 'JPEG'
    elif 'image/png' in content_type:
        return '.png', 'PNG'
    elif 'image/svg+xml' in content_type:
        return '.jpg', 'JPEG'  
    else:
        path = urlparse(url).path
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            return '.jpg', 'JPEG'
        elif ext == '.png':
            return '.png', 'PNG'
        elif ext == '.svg':
            return '.jpg', 'JPEG'
        else:
            return '.jpg', 'JPEG' 

def download_images(url, count, save_dir):

    os.makedirs(save_dir, exist_ok=True)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '').lower()
        extension, img_format = get_extension_and_format(url, content_type)

        if 'image/svg+xml' in content_type or url.lower().endswith('.svg'):
            png_bytes = cairosvg.svg2png(bytestring=response.content)
            img = Image.open(io.BytesIO(png_bytes)).convert('RGB')
        else:
            img = Image.open(io.BytesIO(response.content))

            if img.mode == 'P' and 'transparency' in img.info:
                img = img.convert('RGBA')
            else:
                img = img.convert('RGB')

        filename = os.path.join(save_dir, f'{count}{extension}')
        img.save(filename, img_format)

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 403:
            print(f"Skipped (403 Forbidden): {url}")
        else:
            print(f"HTTP error occurred for {url}: {http_err}")

    except Exception as err:
        print(f"Failed to process {url}: {err}")


def download_all_links(base_dir='data/images_link', save_root='data/downloaded_images'):

    os.makedirs(save_root, exist_ok=True)

    for domain in tqdm(os.listdir(base_dir)):
        domain_path = os.path.join(base_dir, domain)
        if not os.path.isdir(domain_path):
            continue
        
        print(f"Downloading {domain} domain images...")

        for txt_file in os.listdir(domain_path):
            
            if not txt_file.endswith('.txt'):
                continue

            label = os.path.splitext(txt_file)[0]
            txt_path = os.path.join(domain_path, txt_file)
            print('\t', label)

            with open(txt_path, 'r') as f:
                links = [line.strip() for line in f if line.strip()]

            save_dir = os.path.join(save_root, domain, label)
            os.makedirs(save_dir, exist_ok=True)

            image_count = [f"{i:07d}" for i in range(1, len(links) + 1)]

            for i, url in enumerate(tqdm(links)):
                download_images(url, image_count[i], save_dir)


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

    for dirpath, _, filenames in os.walk(src_root):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in valid_extensions:
                src_path = os.path.join(dirpath, filename)

                relative_path = os.path.relpath(dirpath, src_root)
                dst_dir = os.path.join(dst_root, relative_path)
                os.makedirs(dst_dir, exist_ok=True)
                dst_path = os.path.join(dst_dir, filename)

                try:
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
                        print(f"Processed: {src_path} -> {dst_path}")
                except Exception as e:
                    print(f"Failed to process {src_path}: {e}")



if __name__ == '__main__':
    download_all_links()
    process_all_links()

