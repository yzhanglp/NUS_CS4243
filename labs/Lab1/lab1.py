""" CS4243 Lab 1: Template Matching
"""

import os
import cv2
import random
import numpy as np
import matplotlib.pyplot as plt
import math

##### Part 1: Image Preprossessing #####

def rgb2gray(img):
    """
    5 points
    Convert a colour image greyscale
    Use (R,G,B)=(0.299, 0.587, 0.114) as the weights for red, green and blue channels respectively
    :param img: numpy.ndarray (dtype: np.uint8)
    :return img_gray: numpy.ndarray (dtype:np.uint8)
    """
    if len(img.shape) != 3:
        print('RGB Image should have 3 channels')
        return
    
    """ Your code starts here """
    img_gray = img[:, :, 0] * 0.299 + img[:, :, 1] * 0.587 + img[:, :, 2] * 0.114
    """ Your code ends here """
    return img_gray


def gray2grad(img):
    """
    5 points
    Estimate the gradient map from the grayscale images by convolving with Sobel filters (horizontal and vertical gradients) and Sobel-like filters (gradients oriented at 45 and 135 degrees)
    The coefficients of Sobel filters are provided in the code below.
    :param img: numpy.ndarray
    :return img_grad_h: horizontal gradient map. numpy.ndarray
    :return img_grad_v: vertical gradient map. numpy.ndarray
    :return img_grad_d1: diagonal gradient map 1. numpy.ndarray
    :return img_grad_d2: diagonal gradient map 2. numpy.ndarray
    """
    sobelh = np.array([[-1, 0, 1], 
                       [-2, 0, 2], 
                       [-1, 0, 1]], dtype = float)
    sobelv = np.array([[-1, -2, -1], 
                       [0, 0, 0], 
                       [1, 2, 1]], dtype = float)
    sobeld1 = np.array([[-2, -1, 0],
                        [-1, 0, 1],
                        [0,  1, 2]], dtype = float)
    sobeld2 = np.array([[0, -1, -2],
                        [1, 0, -1],
                        [2, 1, 0]], dtype = float)
    

    """ Your code starts here """ 
    def convolution_gray(img, filter):
        filter_height, filter_width = filter.shape
        img_height, img_width = img.shape
        output_height = img_height - filter_height + 1
        output_width = img_width - filter_width + 1
        output = np.zeros((output_height, output_width), dtype=np.float64)

        conv_filter = np.zeros((filter_height, filter_width), dtype=np.float64)
        for i in range(filter_height):
            for j in range(filter_width):
                conv_filter[i, j] = filter[filter_height-1-i, filter_width-1-j]
        # Performing convolution
        for i in range(output_height):
            for j in range(output_width):
                output[i, j] = np.sum(img[i:i+filter_height, j:j+filter_width] * conv_filter)

        return output

    img = pad_zeros(img, 1, 1, 1, 1)
    img_grad_h = convolution_gray(img, sobelh)
    img_grad_v = convolution_gray(img, sobelv)
    img_grad_d1 = convolution_gray(img, sobeld1)
    img_grad_d2 = convolution_gray(img, sobeld2)
    """ Your code ends here """
    return img_grad_h, img_grad_v, img_grad_d1, img_grad_d2


def pad_zeros(img, pad_height_bef, pad_height_aft, pad_width_bef, pad_width_aft):
    """
    5 points
    Add a border of zeros around the input images so that the output size will match the input size after a convolution or cross-correlation operation.
    e.g., given matrix [[1]] with pad_height_bef=1, pad_height_aft=2, pad_width_bef=3 and pad_width_aft=4, obtains:
    [[0 0 0 0 0 0 0 0]
    [0 0 0 1 0 0 0 0]
    [0 0 0 0 0 0 0 0]
    [0 0 0 0 0 0 0 0]]
    :param img: numpy.ndarray
    :param pad_height_bef: int
    :param pad_height_aft: int
    :param pad_width_bef: int
    :param pad_width_aft: int
    :return img_pad: numpy.ndarray. dtype is the same as the input img. 
    """
    height, width = img.shape[:2]
    new_height, new_width = (height + pad_height_bef + pad_height_aft), (width + pad_width_bef + pad_width_aft)
    img_pad = np.zeros((new_height, new_width)) if len(img.shape) == 2 else np.zeros((new_height, new_width, img.shape[2]))

    """ Your code starts here """
    if len(img.shape) == 2:
        img_pad = np.zeros((new_height, new_width), dtype=img.dtype)
        img_pad[pad_height_bef:pad_height_bef+height, pad_width_bef:pad_width_bef+width] = img
    else:
        channels = img.shape[2]
        img_pad = np.zeros((new_height, new_width, channels), dtype=img.dtype)
        img_pad[pad_height_bef:pad_height_bef+height, pad_width_bef:pad_width_bef+width, :] = img
    """ Your code ends here """
    return img_pad




##### Part 2: Normalized Cross Correlation #####
def normalized_cross_correlation(img, template):
    """
    10 points.
    Implement the cross-correlation operation in a naive 4, 5 or 6 nested for-loops. 
    The loops should at least include the height and width of the output and height and width of the template.
    When it is 5 or 6 loops, the channel of the output and template may be included.
    :param img: numpy.ndarray.
    :param template: numpy.ndarray.
    :return response: numpy.ndarray. dtype: float
    """
    Hi, Wi = img.shape[:2]
    Hk, Wk = template.shape[:2]
    #output size
    Ho = Hi - Hk + 1 
    Wo = Wi - Wk + 1
    #template size
    """ Your code starts here """
    response = np.zeros((Ho, Wo), dtype=np.float64)

    for i in range(Ho):
        for j in range(Wo): 
            x=0
            patch_norm = np.linalg.norm(img[i:i+Hk, j:j+Wk, :])
            template_norm = np.linalg.norm(template)
            for k in range(Hk):
                for l in range(Wk):
                    for channel in range(len(img.shape)):
                        x += (img[i+k, j+l, channel]/patch_norm) * (template[k, l, channel]/template_norm)
            response[i, j] = x
    """ Your code  ends here """
    return response


def normalized_cross_correlation_fast(img, template):
    """
    10 points.
    Implement the cross correlation with 3 nested for-loops. 
    The for-loop over the template is replaced with the element-wise multiplication between the kernel and the image regions.
    :param img: numpy.ndarray
    :param template: numpy.ndarray
    :return response: numpy.ndarray. dtype: float
    """
    Hi, Wi = img.shape[:2]
    Hk, Wk = template.shape[:2]
    Ho = Hi - Hk + 1
    Wo = Wi - Wk + 1
    response = np.zeros((Ho, Wo), dtype=np.float64)
    """ Your code starts here """
    template_norm = np.linalg.norm(template)

    for i in range(Ho):
        for j in range(Wo):
            img_patch = img[i:i+Hk, j:j+Wk]
            img_patch_norm = np.linalg.norm(img_patch)
            similarity = np.sum((img_patch/img_patch_norm) * (template/template_norm) )
            response[i, j] = similarity
  
    """ Your code ends here """
    return response




def normalized_cross_correlation_matrix(img, template):
    """
    10 points.
    Converts cross-correlation into a matrix multiplication operation to leverage optimized matrix operations.
    Please check the detailed instructions in the pdf file.
    :param img: numpy.ndarray
    :param template: numpy.ndarray
    :return response: numpy.ndarray. dtype: float
    """
    Hi, Wi= img.shape[:2]
    Hk, Wk = template.shape[:2]
    Ho = Hi - Hk + 1
    Wo = Wi - Wk + 1

    """ Your code starts here """
    channel = img.shape[2]
    Pr = np.zeros((Ho * Wo, Hk * Wk * channel), dtype=np.float64)
    Fr = np.zeros((Hk * Wk*channel, 1), dtype=np.float64)

    for i in range(Pr.shape[0]):
        img_row = i // Wo
        img_col = i % Wo
        img_patch = img[img_row:img_row+Hk, img_col:img_col+Wk]
        Pr[i] = img_patch.flatten()
    for i in range(Fr.shape[0]):
        Fr[i, 0] = template[i // (Wk * channel), (i // channel) % Wk, i % channel]
    Fr = Fr / np.linalg.norm(Fr)
    Pr = Pr / np.linalg.norm(Pr, axis=1, keepdims=True)

    response = np.matmul(Pr,Fr).reshape(Ho,Wo)

    """ Your code ends here """
    return response


##### Part 3: Non-maximum Suppression #####

def non_max_suppression(response, suppress_range, threshold=None):
    """
    10 points
    Implement the non-maximum suppression for translation symmetry detection
    The general approach for non-maximum suppression is as follows:
	1. Set a threshold τ; values in X<τ will not be considered.  Set X<τ to 0.  
    2. While there are non-zero values in X
        a. Find the global maximum in X and record the coordinates as a local maximum.
        b. Set a small window of size w×w points centered on the found maximum to 0.
	3. Return all recorded coordinates as the local maximum.
    :param response: numpy.ndarray, output from the normalized cross correlation
    :param suppress_range: a tuple of two ints (H_range, W_range). 
                           the points around the local maximum point within this range are set as 0. In this case, there are 2*H_range*2*W_range points including the local maxima are set to 0
    :param threshold: int, points with value less than the threshold are set to 0
    :return res: a sparse response map which has the same shape as response
    """
    
    """ Your code starts here """
    max_value = np.max(response)
    response[response < threshold] = 0
    res = np.zeros_like(response)
    while max_value > 0:
        max_index = np.unravel_index(np.argmax(response, axis=None), res.shape)
        if(max_index[0] - suppress_range[0] < 0):
            left =0
        else:
            left = max_index[0]-suppress_range[0]
        if(max_index[1] - suppress_range[1] < 0):
            left2 =0
        else:
            left2 = max_index[1]-suppress_range[1]
        response[left:max_index[0]+suppress_range[0], left2:max_index[1]+suppress_range[1]] = 0
        res[max_index] = 1
        max_value = np.max(response)

    """ Your code ends here """
    return res

##### Part 4: Question And Answer #####
    
def normalized_cross_correlation_ms(img, template):
    """
    10 points
    Please implement mean-subtracted cross correlation which corresponds to OpenCV TM_CCOEFF_NORMED.
    For simplicty, use the "fast" version.
    :param img: numpy.ndarray
    :param template: numpy.ndarray
    :return response: numpy.ndarray. dtype: float
    """
    Hi, Wi = img.shape[:2]
    Hk, Wk = template.shape[:2]
    Ho = Hi - Hk + 1
    Wo = Wi - Wk + 1

    """ Your code starts here """
    response = np.zeros((Ho, Wo), dtype=np.float64)
    """ Your code starts here """
    template_mean = np.mean(template,axis=(0,1))
    template = template - template_mean
    template_norm = np.linalg.norm(template)

    for i in range(Ho):
        for j in range(Wo):
            img_patch = img[i:i+Hk, j:j+Wk]
            img_mean = np.mean(img_patch,axis=(0,1))
            img_patch = img_patch - img_mean
            img_patch_norm = np.linalg.norm(img_patch)
            similarity = np.sum((img_patch/img_patch_norm) * (template/template_norm) )
            response[i, j] = similarity
    img_mean = np.mean(img,axis=(0,1))
    template_mean = np.mean(template,axis=(0,1))

    """ Your code ends here """
    return response




"""Helper functions: You should not have to touch the following functions.
"""
def read_img(filename):
    '''
    Read HxWxC image from the given filename
    :return img: numpy.ndarray, size (H, W, C) for RGB. The value is between [0, 255].
    '''
    img = cv2.imread(filename)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def show_imgs(imgs, titles=None):
    '''
    Display a list of images in the notebook cell.
    :param imgs: a list of images or a single image
    '''
    if isinstance(imgs, list) and len(imgs) != 1:
        n = len(imgs)
        fig, axs = plt.subplots(1, n, figsize=(15,15))
        for i in range(n):
            axs[i].imshow(imgs[i], cmap='gray' if len(imgs[i].shape) == 2 else None)
            if titles is not None:
                axs[i].set_title(titles[i])
    else:
        img = imgs[0] if (isinstance(imgs, list) and len(imgs) == 1) else imgs
        plt.figure()
        plt.imshow(img, cmap='gray' if len(img.shape) == 2 else None)

def show_img_with_points(response, img_ori=None):
    '''
    Draw small red rectangles of size defined by rec_shape around the non-zero points in the image.
    Display the rectangles and the image with rectangles in the notebook cell.
    :param response: numpy.ndarray. The input response should be a very sparse image with most of points as 0.
                     The response map is from the non-maximum suppression.
    :param img_ori: numpy.ndarray. The original image where response is computed from
    :param rec_shape: a tuple of 2 ints. The size of the red rectangles.
    '''
    response = response.copy()
    if img_ori is not None:
        img_ori = img_ori.copy()

    xs, ys = response.nonzero()
    for x, y in zip(xs, ys):
        response = cv2.circle(response, (y, x), radius=0, color=(255, 0, 0), thickness=5)
        if img_ori is not None:
            img_ori = cv2.circle(img_ori, (y, x), radius=0, color=(255, 0, 0), thickness=5)
        
    if img_ori is not None:
        show_imgs([response, img_ori])
    else:
        show_imgs(response)


