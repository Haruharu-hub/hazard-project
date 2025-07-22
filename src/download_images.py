import os
import requests
from PIL import Image
import io
import cairosvg
from urllib.parse import urlparse
from tqdm import tqdm
import hashlib

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
                # links = [line.strip() for line in f if line.strip()]
                links = list(dict.fromkeys(line.strip() for line in f if line.strip()))

            save_dir = os.path.join(save_root, domain, label)
            os.makedirs(save_dir, exist_ok=True)

            image_count = [f"{i:07d}" for i in range(1, len(links) + 1)]

            for i, url in enumerate(tqdm(links)):
                download_images(url, image_count[i], save_dir)

if __name__ == '__main__':
    download_all_links()

