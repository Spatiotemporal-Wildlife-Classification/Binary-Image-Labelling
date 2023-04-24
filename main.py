import pandas as pd
import numpy as np
import requests
import cv2

binary_labels = {49: 'Present', 48: 'Absent'}
file_name = 'wildlife_presence.csv'
data_path = 'data/'


# Aggregate multiple datasets
def aggregate_datasets(datasets: list) -> pd.DataFrame:
    df = pd.DataFrame()
    for dataset in datasets:
        current_df = pd.read_csv(data_path + 'raw/' + dataset, index_col=0)
        current_df = current_df[current_df['taxon_species_name'] != 'Felis catus']
        df = pd.concat([df, current_df],
                       sort=False)
    return df


def generate_url_id_combinations(df: pd.DataFrame):
    ids = df.index.tolist()
    urls = df['image_url'].tolist()
    return ids, urls


def remove_already_processed_observations(df: pd.DataFrame):
    df_labelled = pd.read_csv(data_path + 'labelled/' + file_name)
    labelled_ids = df_labelled['id'].tolist()

    df = df.drop(labelled_ids)
    return df


def process(ids, urls):
    batch = 10
    batch_index = 0

    labels = []
    processed_ids = []

    for id, url in zip(ids, urls):
        download_image(id, url)  # Download the image
        encoded_label = display_image(id)  # Display image
        label = binary_labels[encoded_label]  # Decode the label
        labels.append(label)  # Append the labels to a list
        processed_ids.append(id)
        print(label)

        if batch_index == batch:
            write_to_file(processed_ids, labels)
            batch_index = 0

        batch_index += 1

    write_to_file(ids, labels)


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
    # Import dataframe
    df = aggregate_datasets(['proboscidia_final.csv', 'felids_final.csv'])
    df = remove_already_processed_observations(df)
    print(df.head())

    # Generate id and url list
    ids, urls = generate_url_id_combinations(df)

    # Activate process
    process(ids, urls)