# Binary Image Labelling
A simple binary labelling processor for iNaturalist observation images. 

## Use Cases
The thesis study initially made use of this repository to explore the possibility of using binary 
labelling to train a image classification model capable of classifying the quality of an image, 
or the possibly of classifying whether an animal was present or absent within an image. 

The quality or the presence labelled images were not required in the thesis due to the use of the 
[Mega-detector](https://github.com/microsoft/CameraTraps/blob/main/megadetector.md) YOLO5 object-detection model.

It could be used to supplement the model by evaluating the sub-images as `good` or `bad` quality. 
As with classification models "trash in = trash out". Unfortunately the time constraints of the thesis meant this possibility
was not utilized within the study. But the repository is created to help those needing an efficient system of binary labelling images. 

## How to use
Please perform the following steps in order to use the Binary Labeller:
1. Please ensure the images you wish to label are within the `data/images/` directory.
2. Please specify the labels to be used in line 25
    ```angular2html
    {49: <Positive label>, 48: <Negative label>, 32: 'Ignore'} 
    ```
    
    An example is provided below for the Present/ Absent scenario:
    ```angular2html
    {49: 'Present', 48: 'Absent', 32: 'Ignore'} 
    ```
3. Please specify the name of the file recording the labels for each image. This is on line 20
    ```angular2html
    labelled_file = <file_name>.csv
    ```
     An example for the wildlife presence is below:
     ```
    labelled_file = 'wildlife_presence.csv'
     ```

4. Execute the script
5. The image will be displayed. Select `1` if it fits your positive class. Select `0` if it fits your negative class.
    - The next image will be displayed straight after you have decided your label.
6. To exit the program click any buttion (Not `1`, `0`, or spacebar)
7. The images have been placed in the binary directories in `data/labelled/images/` and also recorded in the `<file name>.csv` in `data/labelled/`.


## Useful Extras

### Ignoring an image you are unsure of
If an image if displayed where you are unsure of the binary class, an **Ignore** feature has been included.
Simply press the **spacebar** key and the image will be skipped. It will not be added to the labelling history nor the binary repositories.

### Ignoring a class
If your dataset is imbalanced and you are attempting to even the binary labels.
Specify on line 32, the name of the class you wish to ignore. Continue labelling as normal, this class
will simply not be recorded.

Example of the wildlife presence, where wildlife is present a lot more that absent.
```angular2html
ignore_class = 'Present'
```