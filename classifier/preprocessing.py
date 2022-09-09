import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from skimage.io import imread
from skimage import color
from skimage.transform import rescale, resize, downscale_local_mean, rotate

import constants as const

class Importer():
    def __init__(self, directory, label):
        self.directory = directory
        self.label = label
        self.image_registry = pd.read_csv(self.directory + const.IMAGE_REGISTRY_EXT, index_col = const.ID_COL)
        self.import_df = pd.DataFrame(columns=const.IMPORT_DF_COLS).set_index(const.ID_COL, drop=True)

    def import_and_augment(self):
        for idx in self.image_registry.index:
            img_path = self.image_registry.loc[idx, const.LOCAL_PATH_COL]
            try:
                original_image = imread(img_path)
            except FileNotFoundError as e:
                continue
            bw_resized_image = color.rgb2gray(resize(original_image, (150,150)))
            rotations_dict = self.obtain_rotated_images(bw_resized_image)
            bw_resized_reflected_image = np.flip(bw_resized_image)
            reflection_rotations_dict = self.obtain_rotated_images(bw_resized_reflected_image)
            rows = []
            for k,v in rotations_dict.items():
                id = f"{idx}_{k}"
                rows.append({const.ID_COL:id, const.LOCAL_PATH_COL:img_path, const.ARRAY_COL: v, const.LABEL_COL: self.label})
            for k,v in reflection_rotations_dict.items():
                id = f"{idx}_r_{k}"
                rows.append({const.ID_COL:id, const.LOCAL_PATH_COL:img_path, const.ARRAY_COL: v, const.LABEL_COL: self.label})
            self.import_df = pd.concat([self.import_df, pd.DataFrame(rows).set_index(const.ID_COL, drop=True)], ignore_index=False)


    def obtain_rotated_images(self, img, angle_list=const.ANGLE_LIST):
        return {angle: rotate(img, angle=angle) for angle in angle_list}

