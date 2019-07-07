import os
import shutil

import numpy as np

from config import (
    BATCH_SIZE, DATA_GEN_ARGS, IMAGE_COLORMODE, MASK_COLORMODE,
    PCA_COLOR_RANGE, TARGET_SIZE, SAMPLE_SIZE)
from keras.preprocessing.image import ImageDataGenerator


def test_generator(dataset_dir, outdir):
    gen_test_dir = os.path.join(outdir, 'GenConfigTest')
    image_dir = os.path.join(gen_test_dir, 'image')
    mask_dir = os.path.join(gen_test_dir, 'mask')

    if os.path.exists(gen_test_dir):
        shutil.rmtree(gen_test_dir)

    os.makedirs(gen_test_dir)
    os.makedirs(image_dir)
    os.makedirs(mask_dir)

    customGen = ImageMaskGenerator(batch_size=20,
                                   dataset_dir=dataset_dir,
                                   folder='train',
                                   aug_dict=DATA_GEN_ARGS,
                                   image_colormode=IMAGE_COLORMODE,
                                   mask_colormode=MASK_COLORMODE,
                                   target_size=TARGET_SIZE,
                                   sample_size=SAMPLE_SIZE,
                                   shuffle=True)


def ImageMaskGenerator(batch_size, dataset_dir, folder, aug_dict,
                       image_colormode, mask_colormode,
                       target_size, sample_size, shuffle):
    seed = np.random.randint(999)

    if image_colormode == 'L':
        image_colormode = 'grayscale'
    elif image_colormode == 'RGB':
        image_colormode = 'rgb'
    else:
        raise Exception('Invalid image colormode')

    if mask_colormode == 'L':
        mask_colormode = 'grayscale'
    elif mask_colormode == 'RGB':
        mask_colormode = 'rgb'
    else:
        raise Exception('Invalid mask colormode')

    if not aug_dict:
        aug_dict = dict(rescale=1./255)

    train_path = os.path.join(dataset_dir, folder)

    image_datagen = ImageDataGenerator(**aug_dict)
    mask_datagen = ImageDataGenerator(**aug_dict)

    imageGen = image_datagen.flow_from_directory(
        train_path,
        classes=['image'],
        class_mode=None,
        color_mode=image_colormode,
        target_size=target_size,
        batch_size=batch_size,
        shuffle=shuffle,
        seed=seed)

    maskGen = mask_datagen.flow_from_directory(
        train_path,
        classes=['mask'],
        class_mode=None,
        color_mode=mask_colormode,
        target_size=target_size,
        batch_size=batch_size,
        shuffle=shuffle,
        seed=seed)

    imagemaskGen = zip(imageGen, maskGen)
    for images, masks in imagemaskGen:
        #: 任意の処理を挟むことが可能
        for i in range(images.shape[0]):
            image = images[i, :, :, :]
            mask = masks[i, :, :, :]

            image, mask = resampling(image, mask)
            if IMAGE_COLORMODE == 'RGB':
                image = pca_color_augmentation_rgb(image)
            elif IMAGE_COLORMODE == 'L':
                image = pca_color_augmentation_L(image)

            mask = adjustmask(mask)

        yield (images, masks)


def resampling(image, mask):
    h = image.shape[0]
    w = image.shape[1]

    upperleft = (np.random.randint(0, h-SAMPLE_SIZE[0]+1), np.random.randint(0, w-SAMPLE_SIZE[1]+1))

    image = image[upperleft[0]:upperleft[0]+SAMPLE_SIZE[0], upperleft[1]:upperleft[1]+SAMPLE_SIZE[1], :]
    mask = mask[upperleft[0]:upperleft[0]+SAMPLE_SIZE[0], upperleft[1]:upperleft[1]+SAMPLE_SIZE[1], :]

    return image, mask


def pca_color_augmentation_rgb(image_array_input):
    """
        RGBカラー画像限定
        コピぺ：https://qiita.com/koshian2/items/78de8ccd09dd2998ddfc
    """

    img = image_array_input.reshape(-1, 3).astype(np.float32)
    # 分散を計算
    ch_var = np.var(img, axis=0)
    # 分散の合計が3になるようにスケーリング
    scaling_factor = np.sqrt(3.0 / sum(ch_var))
    # 平均で引いてスケーリング
    img = (img - np.mean(img, axis=0)) * scaling_factor

    cov = np.cov(img, rowvar=False)
    lambd_eigen_value, p_eigen_vector = np.linalg.eig(cov)

    while True:
        rand = np.random.randn(3) * 0.1
        if np.all(rand > PCA_COLOR_RANGE[0]):
            if np.all(rand < PCA_COLOR_RANGE[1]):
                break

    delta = np.dot(p_eigen_vector, rand*lambd_eigen_value)
    delta = (delta * 255.0).astype(np.int32)[np.newaxis, np.newaxis, :]

    img_out = np.clip(image_array_input + delta, 0, 255).astype(np.uint8)
    return img_out
