# Binary Image Labelling
A simple binary labelling processor for images downloaded through a URL. 

## This repository serves as a functional Tool to aid in the the bachelor Thesis investigating the 
capability of meta-data usage in combination with wildlife image classification. For more information please review 
https://github.com/trav-d13/spatiotemporal_wildlife_classification.

In order to use this simple program, simply execute the main method. 
An image will be presented as a pop-up. Please select enter `1` for the positive case (Present/ Good), 
or alternatively press 0 for the negative case (Absent/ Bad). 

### Use cases
#### Wildlife Presence Classifier
Label images with `Present` or `Absent` in order to create a dataset, whereby the aim is to determine a pre-processing classifier capable
of detecting if an image contains an animal within it. 

Please specify the file_name within main. 
Additionally, please ensure the binary labels are `Present` or `Absent` at line 6. 


#### Wildlife Image Quality Classifier
Label images with `Good` or `Bad` quality, in order to generate a dataset, whereby the aim is to generate a model
capable of assessing the quality of an image, as a preprocessing step before wildlife classification.

Please specify the file_name within main. 
Additionally, please ensure the binary labels are `Good` or `Bad` at line 6. 