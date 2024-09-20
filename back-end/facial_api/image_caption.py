import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import cv2
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

# img_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/demo.jpg' 



def main_image_caption(image):

    # img = Image.fromarray(frame)
    # raw_image = Image.open(img_path).convert('RGB')
    
    img = Image.fromarray(image)
    if img.mode != 'RGB':
        img = img.convert(mode="RGB")
    # conditional image captioning
    text = ""
    inputs = processor(img, text, return_tensors="pt")

    # No raw_image = Imager.open(img_path).convert('RGB')
    out = model.generate(**inputs)
    caption_result = processor.decode(out[0], skip_special_tokens=True)

    # # unconditional image captioning
    # inputs = processor(img, return_tensors="pt")

    # out = model.generate(**inputs)
    # caption_result = processor.decode(out[0], skip_special_tokens=True)


    return caption_result