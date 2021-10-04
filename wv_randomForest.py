# Random forest for worldview change
import numpy as np
import rasterio
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# fp = r'Y:\gis_lab\project\USFWS\change_analysis\stclair\segmentation\stClair2014_2019_ang_mag_GVI_segment.tif'
fp = r'D:\Users\afpoley\Desktop\stClair2014_2019_ang_mag_GVI_segment.tif'
fp_out = r'D:\Users\afpoley\Desktop\stClair2014_2019_ang_mag_GVI_segment_classified.tif'
fp_ref = r'D:\Users\afpoley\Desktop\hybrid_polygon.csv'
change_threshold = 0.4


def open_raster(rst_fp):
    with rasterio.open(rst_fp) as src:
        src_meta = src.meta
        rst = src.read()
    return rst, src_meta


training = np.genfromtxt(fp_ref, delimiter=',')
labels = training[1:, 0]
values = training[1:, 1:]
unique_classes = np.unique(training[:, 1])


# open image and reshape
img, meta = open_raster(fp)
img = img[0:3, :, :]
img_NANs = np.isnan(np.where(img[0, :, :] < change_threshold, np.nan, img[0, :, :]))     # mask out non-change areas
img = np.where(img_NANs == True, 0, img[:, :, :])
img = img.transpose(1, 2, 0).reshape(-1, 3)

X_train, X_test, y_train, y_test = train_test_split(values, labels, test_size=0.2)
clf = RandomForestClassifier()
clf.fit(X_train, y_train)
classified = clf.predict(img)
class_accuracy = clf.predict(X_test)
print("Accuracy:", accuracy_score(y_test, class_accuracy))

classified = classified.reshape(meta['height'], meta['width'])
classified = classified.astype(np.int32)
classified = np.where(img_NANs == True, 0, classified[:, :])

meta.update({"driver": "GTiff",
             "height": classified.shape[0],
             "width": classified.shape[1],
             "dtype": np.int32,
             "count": 1})

with rasterio.open(fp_out, "w", **meta) as dest:
    dest.write(classified, 1)

