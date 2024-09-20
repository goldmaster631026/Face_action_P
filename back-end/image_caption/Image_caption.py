from transformers import VisionEncoderDecoderModel, ViTFeatureExtractor, AutoTokenizer
import torch
from PIL import Image

model_name = "bipin/image-caption-generator"
model = VisionEncoderDecoderModel.from_pretrained(model_name)
feature_extractor = ViTFeatureExtractor.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained("gpt2")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

img_name = "input/1.png"
img = Image.open(img_name)
if img.mode != 'RGB':
    img = img.convert(mode="RGB")

pixel_values = feature_extractor(images=[img], return_tensors="pt").pixel_values
pixel_values = pixel_values.to(device)

max_length = 128
num_beams = 4
output_ids = model.generate(pixel_values, num_beams=num_beams, max_length=max_length)

# Flatten the list of token IDs
output_ids = output_ids[0].tolist()

preds = tokenizer.decode(output_ids, skip_special_tokens=True)
print(preds)