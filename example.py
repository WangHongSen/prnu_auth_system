# -*- coding: UTF-8 -*-
"""
@author: Luca Bondi (luca.bondi@polimi.it)
@author: Paolo Bestagini (paolo.bestagini@polimi.it)
@author: Nicolò Bonettini (nicolo.bonettini@polimi.it)
Politecnico di Milano 2018
"""

import os
from glob import glob
from multiprocessing import cpu_count, Pool

import numpy as np
from PIL import Image

import prnu
import shelve

def main():
    """
    Main example script. Load a subset of flatfield and natural images from Dresden.
    For each device compute the fingerprint from all the flatfield images.
    For each natural image compute the noise residual.
    Check the detection performance obtained with cross-correlation and PCE
    :return:
    """
    ff_dirlist = np.array(sorted(glob('test/data/myff-jpg/*.JPG')))
    ff_device = np.array([os.path.split(i)[1].rsplit('_', 1)[0] for i in ff_dirlist])
    
    nat_dirlist = np.array(sorted(glob('test/data/mynat-jpg/*.JPG')))
    nat_device = np.array([os.path.split(i)[1].rsplit('_', 1)[0] for i in nat_dirlist])
    print(nat_dirlist)
    print('Computing fingerprints')
    fingerprint_device = sorted(np.unique(ff_device))
    print(fingerprint_device)
    k = []
    prnu_cache = shelve.open('cache/PRNU')
    for device in fingerprint_device:
        imgs = []
        imgs_mark = ""
        for img_path in ff_dirlist[ff_device == device]:
            imgs_mark += img_path       
            im = Image.open(img_path)
            im_arr = np.asarray(im)
            if im_arr.dtype != np.uint8:
                print('Error while reading image: {}'.format(img_path))
                continue
            if im_arr.ndim != 3:
                print('Image is not RGB: {}'.format(img_path))
                continue
            im_cut = prnu.cut_ctr(im_arr, (2048, 2048, 3))
            imgs += [im_cut]  
        try:
            PRNU = prnu_cache[imgs_mark]
            k += PRNU 
        except:
            PRNU = [prnu.extract_multiple_aligned(imgs, processes=cpu_count())]
            k += PRNU
            prnu_cache[imgs_mark] = PRNU
    k = np.stack(k, 0)
    prnu_cache.close()
    #print('Computing residuals')
    imgs = []
    noise_cache = shelve.open('cache/noise')
    for img_path in nat_dirlist:
        try:
            residuals = noise_cache[img_path]
            imgs += residuals
        except:
            residuals = [prnu.cut_ctr(np.asarray(Image.open(img_path)), (2048, 2048, 3))]
            imgs += residuals
            noise_cache[img_path] = residuals
    noise_cache.close()
    pool = Pool(cpu_count())
    w = pool.map(prnu.extract_single, imgs)
    pool.close()

    w = np.stack(w, 0)

    # Computing Ground Truth
    gt = prnu.gt(fingerprint_device, nat_device)
    print(np.array(gt).transpose())
    print(len(k[0][0]))
   #print(w)
    print('Computing cross correlation')
    cc_aligned_rot = prnu.aligned_cc(k, w)['cc']
    print(np.array(cc_aligned_rot).transpose())

    print('Computing statistics cross correlation')
    stats_cc = prnu.stats(cc_aligned_rot, gt)

    print('Computing PCE')
    pce_rot = np.zeros((len(fingerprint_device), len(nat_device)))
    
    for fingerprint_idx, fingerprint_k in enumerate(k):
        for natural_idx, natural_w in enumerate(w):
            cc2d = prnu.crosscorr_2d(fingerprint_k, natural_w)
            pce_rot[fingerprint_idx, natural_idx] = prnu.pce(cc2d)['pce']
    print(np.array(pce_rot).transpose())
    print('Computing statistics on PCE')
    stats_pce = prnu.stats(pce_rot, gt)
    
    print('AUC on CC {:.2f}, expected {:.2f}'.format(stats_cc['auc'], 0.98))
    print('AUC on PCE {:.2f}, expected {:.2f}'.format(stats_pce['auc'], 0.81))

if __name__ == '__main__':
    main()
