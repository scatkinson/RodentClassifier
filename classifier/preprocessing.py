import matplotlib.pyplot as plt
import pandas as pd
from skimage.io import imread
from skimage import color
from skimage.transform import rescale, resize, downscale_local_mean, rotate

test_image_path = "data/guineapigs/images/" + "cjrxqwqj4h01.jpg"

original_image = imread(test_image_path)
plt.imshow(original_image)
# plt.show()

bw_image = color.rgb2gray(original_image)
plt.imshow(bw_image, cmap='gray')
# plt.show()

resized_bw_image = resize(bw_image, (150,150))
plt.imshow(resized_bw_image, cmap='gray')
# plt.show()

rotate30 = rotate(resized_bw_image, angle=30)
plt.imshow(rotate30, cmap='gray')
plt.show()
print(type(resized_bw_image))

class Importer():
    def __init__(self, directory, label):
        self.directory = directory
        self.label = label
        self.image_registry = pd.read_csv(self.directory+"image_registry/image_registry.csv", index_col = "id")