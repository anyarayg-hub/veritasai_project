import openml
import pandas as pd

print("Downloading dataset 43373 from OpenML...")
# Download dataset by its OpenML ID (43373)
dataset = openml.datasets.get_dataset(43373)

# Get the data, categorical indicators, and column names
X, y, categorical_indicator, attribute_names = dataset.get_data(
    target=dataset.default_target_attribute,
    dataset_format="dataframe"
)

# Combine features and target into a single DataFrame
df = X.copy()
if y is not None:
    df[dataset.default_target_attribute] = y

# Save to the CSV file you created in the workspace
df.to_csv("dataset_43373.csv", index=False)
print("Dataset successfully downloaded and saved to dataset_43373.csv!")