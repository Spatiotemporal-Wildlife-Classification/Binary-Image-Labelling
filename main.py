"""
    Attributes:
        root_path (str): The absolute path of the project root.
        data_path (str): The complete path (absolute + relative) to the project `data` directory
        observation_path (str) The complete path to the `data/observations/` directory. This directory contains the iNaturalist observations.
        labelled_path (str): The complete path to the `data/labelled/` directory. This directory contains a record of the labelled observations.
"""

import pandas as pd
import cv2
import shutil
import sys
import os

# Paths
root_path = sys.path[1]
data_path = root_path + "/data/"
observation_path = data_path + "observations/"
labelled_path = data_path + "labelled/"
labelled_file = 'wildlife_presence.csv'
image_path = data_path + "/images/"
labelled_image_path = labelled_path + "images/"

# Label info
binary_labels = {49: 'Present', 48: 'Absent', 32: 'Ignore'}  # Feel free to changes the label names to suit the needs of the binary labelled.

# Binary counts
positive_count = 0
negative_count = 0

# Ignoring class
ignore_class = ''


def aggregate_datasets(datasets: list) -> pd.DataFrame:
    """This method aggregates the specified dataset list into a single dataframe for further use.

    Note, this method can be used if the user requires the images to be matched to a dataset.
    In the current format, the labelling process only requires the images. This method is in place to offer the
    capability to extend the labelling process if required.

    Args:
        datasets (list): A list of dataset file names. These will be aggregated into a single dataframe.

    Returns:
        (DataFrame): A single dataframe comprising the aggregated datasets.
    """
    df = pd.DataFrame()
    for dataset in datasets:  # Iterate through the datasets
        current_df = pd.read_csv(observation_path + dataset, index_col=0)  # Read in the currrent dataset as a dataframe

        current_df = current_df[current_df['taxon_species_name'] != 'Felis catus']  # Apply known Felis catus restriction
        df = pd.concat([df, current_df], sort=False)  # Concatenate the dataframes
    return df


def remove_already_processed_observations(df: pd.DataFrame):
    """This method removes the already labelled observations from the dataset.

    The method accesses the already labelled dataset and extracts the unique observation IDs.
    It removes the IDs if they are present in the current dataset to avoid repetition.

    Additionally, the method updates the positive and negative counts to keep track of the number of each binary label in the
    labelled dataset.

    Note, this method can be used if the user requires the images to be matched to a dataset.
    In the current format, the labelling process only requires the images. This method is in place to offer the
    capability to extend the labelling process if required.

    Args:
        df (DataFrame): The current dataset to still be labelled.

    Returns:
        (DataFrame): The dataframe is returned with already labelled observations removed from it.
    """

    if os.path.exists(labelled_path + labelled_file):
        df_labelled = pd.read_csv(labelled_path + labelled_file)  # Read in the labelled dataset
        labelled_ids = df_labelled['id'].tolist()  # Generate a list of id's in the labelled dataset
        df = df.drop(labelled_ids)  # From the current dataset, drop the rows with the same id (id is the index).

        update_binary_counts(df_labelled)  # Update the binary counts
    else:
        with open(labelled_path + labelled_file, 'w') as file:  # Create an empty file if it doesn't exist
            file.write("id,label\n")

    return df


def update_binary_counts(df_labelled: pd.DataFrame):
    """This method updates the binary counts based on the already labelled data.

    This method updates the global binary counts of the file.

    Args:
        df_labelled (DataFrame): The dataframe containing the already labelled observations.
    """
    global positive_count, negative_count

    if not df_labelled.empty:  # Update the binary label counts if the file is not empty
        counts = df_labelled['label'].value_counts().to_dict()  # Convert counts to a dictionary

        for label in counts.keys():  # Label matching to update counts
            if label == binary_labels[49]:
                positive_count = counts[label]
            elif label == binary_labels[48]:
                negative_count = counts[label]


def labelling_process():
    """This method controls the image labelling process.

    In summary, the process is as follows:
    The `data/images/` directory holds all of the images to be labelled.
    A check is conducted to ensure no images are repeatedly labelled.
    Each image is labelled, the image is copied into a corresponding directory.
    A history of each image filename and its corresponding label is maintained.

    As a result, there exists a `labelled_file.csv` containing the labelling history.
    Additionally, within the `data/labelled/images/` directory there exist two directories housing the binary labelled images.
    """
    filenames = os.listdir(image_path)  # Gather filenames from image directory. It is assumed the filenames are the ID's
    filenames = avoid_duplicate_images(filenames)  # avoid already labelled images

    labelled_files = []  # Storing the labelled files
    labels = []  # Storing the labels

    for filename in filenames:
        encoded_key = display_image(filename)

        try:
            label = binary_labels[encoded_key]  # Decode the label

            if label != ignore_class and label != 'Ignore':  # If the label isn's specified as the ignore class and its not the Ignore label
                labels.append(label)
                labelled_files.append(filename)

                status_update(encoded_key)  # Binary count update
                copy_to_labelled_images(filename, label)  # Copy image to data/labelled/images

        except:
            write_to_file(labelled_files, labels)  # Write the labelling history on exit.
            sys.exit()


def display_image(filename: str):
    """This method displays the image specified by the filename.

    The filename of the image is assumed to be located in the `data/images/` directory.
    The image display will close upon the click of the button to label the image.

    Args:
        filename (str): The file name of the image to be displayed.

    Returns:
        (int): An integer encoding of the key pressed.
    """
    img = cv2.imread(image_path + filename)
    cv2.imshow('Current image', img)
    key_pressed = cv2.waitKey(0)
    return key_pressed


def avoid_duplicate_images(filenames: list):
    """This method removes images from filenames, that have already been processed to avoid repeated work.

    Args:
        filenames (list): The list of all image filenames to be labelled.

    Returns:
        (list): A list of filenames, with those already labelled removed.
    """
    if os.path.exists(labelled_path + labelled_file):
        df_labelled = pd.read_csv(labelled_path + labelled_file)  # Read in the labelled dataset
        labelled_images = df_labelled['id'].tolist()  # Generate a list of id's in the labelled dataset
        filenames = filter(lambda i: i not in labelled_images, filenames)
    else:
        with open(labelled_path + labelled_file, 'w') as file:  # Create an empty file if it doesn't exist
            file.write("id,label\n")

    return filenames


def write_to_file(filenames: list, labels):
    """This method writes the labelled files and their corresponding labels to the `labelled_file`

    Args:
        filenames (list): A list of filenames with the corresponding labels in the same order as the labels list.
        labels (list): The categorical labels of the images.
    """
    results_df = pd.DataFrame({'id': filenames, 'label': labels})
    results_df.to_csv(labelled_path + labelled_file, mode='a', index=False, header=False)


def status_update(encoded_key: int):
    """This method updates the binary counts and displays the current counts to the terminal

    Args:
        encoded_key (int): The encode key value (numerical representation of the key pressed)
    """
    global positive_count, negative_count

    if encoded_key == 49:  # Positive encoding
        positive_count += 1
    elif encoded_key == 48:  # Negative encoding
        negative_count += 1

    print(binary_labels[49] + ' count: ' + str(positive_count) + ', ' +
          binary_labels[48] + ' count: ' + str(negative_count))


def copy_to_labelled_images(filename: str, label: str):
    """This method copies the labelled image to the corresponding directory within `data/labelled/images/`

    Note, the binary directories will be created automatically based on the categorical names provided in the code.
    In the end, the `data/labelled/images/` directory will contain two additional directories housing images of each class.

    Args:
        filename (str): The name of the file to be copied into the labelled images directory.
        label (str): The corresponding categorical label of the image.
    """
    file_origin = image_path + filename
    file_destination_directory = labelled_image_path + label + "/"
    file_destination = file_destination_directory + filename

    if not os.path.exists(file_destination_directory):  # If the directory doesn't exist, then make the directory
        os.makedirs(file_destination_directory)

    shutil.copy(file_origin, file_destination)  # Copy the file from the origin directory into the newly specified directory.


if __name__ == "__main__":
    labelling_process()
