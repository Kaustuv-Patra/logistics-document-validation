from PIL import Image, ImageDraw, ImageFont
import os

ASSETS_DIR = os.path.abspath("data/pdf_assets")

os.makedirs(ASSETS_DIR, exist_ok=True)

def create_image(filename, text):
    img = Image.new("RGB", (300, 100), color="white")
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, 299, 99], outline="black", width=2)
    draw.text((20, 40), text, fill="black")

    img.save(os.path.join(ASSETS_DIR, filename))

def main():
    create_image("logo.png", "COMPANY LOGO")
    create_image("stamp.png", "OFFICIAL STAMP")
    create_image("signature.png", "SIGNATURE")

    print("Dummy PDF assets generated.")

if __name__ == "__main__":
    main()
