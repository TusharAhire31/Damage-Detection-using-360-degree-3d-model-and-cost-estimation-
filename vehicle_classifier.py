import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import os

# Pre-trained ResNet50 model for image classification
model = models.resnet50(pretrained=True)
model.eval()

VEHICLE_LABELS = {
    "car": ["car", "sedan", "sports car", "limousine", "cab"],
    "truck": ["truck", "pickup", "lorry"],
    "bus": ["bus", "coach"],
    "motorcycle": ["motorcycle", "bike", "scooter"],
    "bicycle": ["bicycle", "cycle"],
    "van": ["van", "minivan", "cargo van"]
}

# Transformation pipeline
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
LABELS_PATH = "imagenet_labels.txt"

if not os.path.exists(LABELS_PATH):
    import requests
    labels_text = requests.get(LABELS_URL).text
    with open(LABELS_PATH, "w") as f:
        f.write(labels_text)

with open(LABELS_PATH) as f:
    IMAGENET_LABELS = [line.strip().lower() for line in f.readlines()]


def detect_vehicle_type(image_path: str) -> str:
    """
    Detects vehicle type (car, bike, truck, bus, etc.) from input image.
    """
    image = Image.open(image_path).convert("RGB")
    img_t = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img_t)
        _, index = torch.max(outputs, 1)
        label = IMAGENET_LABELS[index.item()]

    for v_type, keywords in VEHICLE_LABELS.items():
        if any(k in label for k in keywords):
            return v_type.capitalize()

    return "Unknown Vehicle"
