import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn.functional as F
import numpy as np
from PIL import Image

class RecyclePredict:

  def __init__(self) -> None:

    self.model = None
    self.device = None
    self.prediction = None
    self.probabilities = None

  def prep_model(self, classes):

    self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Loading to {self.device}")
    self.model = torchvision.models.resnet18(pretrained=True)
    print(f"Pushing Resnet18 Model to {self.device}")
    self.model.fc = torch.nn.Linear(512, len(classes))
    self.model.to(self.device)
    print("Done...")

  def load_trained_model(self, trained_path):
    print("Loading Your Trained Dataset")
    self.model.load_state_dict(torch.load(trained_path))
    self.model = self.model.eval()
    print("Done...")


  def preprocess_image(self,image):
    print("Preping Image for Prediction")
    mean = torch.Tensor([0.485, 0.456, 0.406]).cuda()
    std = torch.Tensor([0.229, 0.224, 0.225]).cuda()

    image = transforms.functional.to_tensor(image).to(self.device)
    image.sub_(mean[:, None, None]).div_(std[:, None, None])
    print("Done...")
    return image[None, ...]

  def get_probabilities(self, image):
    with torch.no_grad():
      print("Get Probs...")
      output = self.model(image)
      self.probabilities = F.softmax(output, dim=1).detach().cpu().numpy().flatten()
    return self.probabilities

  def get_preduction(self):
    if self.get_probabilities:
      print(("Get Prediction..."))
      self.prediction = self.probabilities.argmax()
    
    return self.prediction

  
  def __del__(self):
    print("Removing Model From GPU")
    torch.cuda.empty_cache()
    print("Program Closed")
  

RECYCLE_TYPE = ["Cardbrd", "Glass", "Metal", "Paper", "Plastic", "Trash"]

img_path = "data/testing_data/test/cardboard/cardboard111.jpg"
path = "data/resnet18_recycle_train.pth"
test = RecyclePredict()
test.prep_model(RECYCLE_TYPE)
test.load_trained_model(path)

import cv2
img = cv2.imread(img_path, cv2.IMREAD_ANYCOLOR)
img = Image.fromarray(img)
img = test.preprocess_image(img)

# with torch.no_grad():
#   output = test.model(img)
#   test.prediction = F.softmax(output, dim=1).detach().cpu().numpy().flatten()

print(test.get_probabilities(img))
i = test.get_preduction()
print(RECYCLE_TYPE[i])
