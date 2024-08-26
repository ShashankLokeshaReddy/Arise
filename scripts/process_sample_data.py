import pandas as pd

# Load the CSV file into a pandas dataframe
df = pd.read_csv('sample_data_arise.csv')

# Add a new column called Job_ID
df['Job_ID'] = range(1, len(df)+1)

# Save the updated dataframe to a new CSV file
df.to_csv('sample_data_arise_job_id.csv', index=False)
