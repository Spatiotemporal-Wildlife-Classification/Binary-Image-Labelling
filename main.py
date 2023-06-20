"""
    Attributes:
        root_path (str): The absolute path of the project root.
        data_path (str): The complete path (absolute + relative) to the project `data` directory
        observation_path (str) The complete path to the `data/observations/` directory. This directory contains the iNaturalist observations.
        labelled_path (str): The complete path to the `data/labelled/` directory. This directory contains a record of the labelled observations.
"""

import pandas as pd
import requests
import cv2
import shutil
import sys
import random
import os

# Paths
root_path = sys.path[1]
data_path = root_path + "/data/"
observation_path = data_path + "observations/"
labelled_path = data_path + "labelled/"
labelled_file = 'wildlife_presence.csv'


binary_labels = {49: 'Present', 48: 'Absent', 32: 'Ignore'}  # Feel free to changes the label names to suit the needs of the binary labelled.
data_path = 'data/'

positive_count = 0
negative_count = 0
ignore_class = ''

test_split = 0.2



def aggregate_datasets(datasets: list) -> pd.DataFrame:
    """This method aggregates the specified dataset list into a single dataframe for further use.

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
            file.write("id,label")

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



def generate_url_id_combinations(df: pd.DataFrame):
    ids = df.index.tolist()
    urls = df['image_url'].tolist()
    return ids, urls

def process(ids, urls):

    labels = []
    processed_ids = []

    for id, url in zip(ids, urls):
        download_image(id, url)  # Download the image
        encoded_label = display_image(id)  # Display image
        try:
            label = binary_labels[encoded_label]  # Decode the label
        except:
            write_to_file(processed_ids, labels)
            sys.exit()
        if label != ignore_class and label != 'Ignore':
            labels.append(label)  # Append the labels to a list
            processed_ids.append(id)
            status_update(encoded_label)  # Status update
            place_image_in_subdirectory(label, id)  # Format image directory sub-structure


def place_image_in_subdirectory(label: str, id):
    current_dir = root_path + '/' + data_path + 'labelled/' + str(id) + '.jpg'

    test_dir = root_path + '/' + data_path + 'labelled/test/' + label + '/' + label + '_image_' + str(id) + '.jpg'
    sub_dir = root_path + '/' + data_path + 'labelled/' + label + '/' + label + '_image_' + str(id) + '.jpg'

    rand_value =  random.uniform(0, 1)
    if rand_value > test_split:
        shutil.move(current_dir, sub_dir)
    else:
        shutil.move(current_dir, test_dir)


def status_update(encoded_label: int):
    global positive_count, negative_count
    if encoded_label == 49:
        positive_count += 1
    elif encoded_label == 48:
        negative_count += 1
    print(binary_labels[49] + ' count: ' + str(positive_count) + ', ' +
          binary_labels[48] + ' count: ' + str(negative_count))


def write_to_file(ids, labels):
    results_df = pd.DataFrame({'id': ids, 'label': labels})
    results_df.to_csv(data_path + 'labelled/' + file_name, mode='a', index=False, header=False)


def display_image(id: str):
    img = cv2.imread(data_path + 'labelled/' + str(id) + '.jpg')
    cv2.imshow('Current image', img)
    key_pressed = cv2.waitKey(0)
    return key_pressed


def download_image(id: str, url: str):
    img_data = requests.get(url).content
    with open(data_path + 'labelled/' + str(id) + '.jpg', 'wb') as handler:
        handler.write(img_data)


if __name__ == "__main__":
    datasets = ['proboscidia_train.csv', 'felids_train.csv']  # Specify the datasets
    df = aggregate_datasets(datasets)  # Aggregate datasets together.

    df = remove_already_processed_observations(df)  # Remove already labelled observations

    # Shuffle rows
    # df = df.sample(frac=1)
    #
    # # Generate id and url list
    # ids, urls = generate_url_id_combinations(df)
    #
    # # Activate process
    # process(ids, urls)