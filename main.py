import pandas as pd
import numpy as np
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


binary_labels = {49: 'Present', 48: 'Absent', 32: 'Ignore'}
file_name = 'wildlife_presence.csv'
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


def generate_url_id_combinations(df: pd.DataFrame):
    ids = df.index.tolist()
    urls = df['image_url'].tolist()
    return ids, urls


def remove_already_processed_observations(df: pd.DataFrame):
    global positive_count, negative_count
    df_labelled = pd.read_csv(data_path + 'labelled/' + file_name)
    print(df_labelled.head())
    labelled_ids = df_labelled['id'].tolist()
    df = df.drop(labelled_ids)

    # Update the positve and negative counts
    if not df_labelled.empty:
        counts = df_labelled['label'].value_counts().to_dict()
        for label in counts.keys():
            if label == binary_labels[49]:
                positive_count = counts[label]
            elif label == binary_labels[48]:
                negative_count = counts[label]

    return df


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

    # df = remove_already_processed_observations(df)
    # Shuffle rows
    # df = df.sample(frac=1)
    #
    # # Generate id and url list
    # ids, urls = generate_url_id_combinations(df)
    #
    # # Activate process
    # process(ids, urls)