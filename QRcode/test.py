from skimage import io,util
img=io.imread('1554611594.3442483_test.png')
img = util.random_noise(img, mode='gaussian', seed=None, clip=True,var=0.5)
io.imsave('test_var=0.5.png',img)


