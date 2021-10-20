Documentation for semi-automated wetland gain, loss, and type change detection.
Poley 10/20/2021

Pre-processing:
1) Normalize worldview images
    * normalize_WV.py
    * Author: Mike Billmire
    * Purpose: Normalize worldview images that cover the same extent to each other
    * Inputs:
      * Reference WV image
      * WV images to be normalized
      * PIF.shp (shapefile in same coordinates as images. White and black features. Shapefile needs a ‘pif’ attribute.)
    * Output:
      * New directory with normalized images including reference image
2) Radiometric change
    * wv_CVA.py
    * Author: Andrew Poley
    * Purpose: calculate change magnitude, angle, and tasseled cap greenness (GVI)
    * Inputs:
      * WV images from year 1 & year 2
      * Output name and directory
    * Output:
      * Single image with 3 bands (magnitude, angle, and GVI
3) Image segmentation
    * Segmentation.py
    * Author: Andrew Poley
    * Purpose: segment radiometric change images using scikit-image SLIC segmentation
    * Inputs:
      * Output image from radiometric change code
      * Output directory
    * Output:
      * Segmented image with mean values for each segment. 4-band image: mean-magnitude, mean-angle, mean-GVI, and segment number
      * NOTE: code takes a very long time to run on larger areas. Run ‘tile_raster.py’ on radiometric change image before running segmentation to speed up processing.
      * Tile raster code needs input image and output directory for image tiles and will create image tiles.
      Input tile directory into segmentation code. Run ‘mosaic_tiles.py’ on segmented tile outputs to re-mosaic the image for the next step.


Wetland Gain/Loss/Type change
1) Wetland_gain_loss.py
    * Author: Andrew Poley
    * Purpose: Calculate wetland gain, loss, and type change from segmented radiometric change
    * Inputs:
        * Mosaiced segmented radiometric change image
        * Change thresholds:
            * CVA magnitude used to determine change/no-change
            * TCG_upper is used to determine wetland gain
            * TCG_lower is used to determine wetland loss
        * Land cover classification of year 1
    * Output:
        * Classified map of wetland gain, loss, and type change
          * -1 = wetland loss
          * 1 = wetland gain
          * 100 = wetland change type


    NOTES:
      * Brief code description
          1) Use provided thresholds to determine change/no change in CVA image
          2) Reclassify land cover classification to only include wetland classes
          3) Intersect change/no-change and wetland classification to estimate which wetlands are changing
          4) Intersect wetland change/no-change with thresholded TCG layer to get gain, loss, and type change
          5) Reclassify change into gain & loss
      * IMPORTANT:
          * Input radiometric change and classification images must be in the same coordinate system and must have the same number of rows and columns.
          * Assumes input classification has been reclassified into the following classes/numbers:
              1 = urban
              2 = suburban
              3 = barren land
              4 = agriculture
              5 = grasslands
              6 = deciduous
              7 = evergreen
              8 = shrubs
              9 = woody wetland
              10 = emergent wetland
              11 = floating aquatic
              12 = water
              13 = detritus
              17 = typha
              18 = phragmites
