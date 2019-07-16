""" Training config
    COLORMODE = Enum(['L', 'RGB'])
"""

IMAGE_COLORMODE = 'L'
MASK_COLORMODE = 'RGB'

"""RGB setting
"""
MASK_USECOLORS = 'RB'
BG_COLOR = False
BACKGROUND_COLOR = [0, 1, 0]

""" 'tversky' or 'categorical cross entropy'
"""
#LOSS = 'categorical_crossentropy'
LOSS = 'tversky'

MODEL = 'unet'

TARGET_SIZE = (256, 256)
SAMPLE_SIZE = (256, 256)
FRAME_SIZE = 32
PCA_COLOR = True

BATCH_SIZE = 4

TRAIN_STEPS = 100
VALID_STEPS = 50
EPOCHS = 30

EA_EPOCHS = 5

#: 基本的にはこの設定値なら影響がない
PCA_COLOR_RANGE = (-0.2, 0.2)

DATA_GEN_ARGS = dict(
    rescale=1./255,
    rotation_range=40,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.0,
    zoom_range=0.1,
    vertical_flip=True,
    horizontal_flip=True,
    cval=0,
    fill_mode='constant')

"""
基本はグレスケ入力-L/RGB出力を想定
未検証：RGB入力

UpSampling2D使用は出力の格子模様を防ぐ
"""
