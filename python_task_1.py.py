# -*- coding: utf-8 -*-
"""Untitled7.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RntLRWCQA5kNO0B1UIVqVRaz-hvCVik4

**Python Task 2:**

Question 1: Distance Matrix Calculation
Create a function named calculate_distance_matrix that takes the dataset-3.csv as input and generates a DataFrame representing distances between IDs.

The resulting DataFrame should have cumulative distances along known routes, with diagonal values set to 0. If distances between toll locations A to B and B to C are known, then the distance from A to C should be the sum of these distances. Ensure the matrix is symmetric, accounting for bidirectional distances between toll locations (i.e. A to B is equal to B to A).
"""

import pandas as pd
import networkx as nx

def calculate_distance_matrix(dataframe):
# Create a directed graph to represent toll locations and distances
G = nx.DiGraph()

# Add edges and their distances to the graph
for _, row in dataframe.iterrows():
    G.add_edge(row['toll_booth_A'], row['toll_booth_B'], distance=row['distance'])
    G.add_edge(row['toll_booth_B'], row['toll_booth_A'], distance=row['distance'])

# Use the Floyd-Warshall algorithm to calculate the shortest paths between all pairs of nodes
distances = nx.floyd_warshall(G, weight='distance')

# Create a DataFrame from the calculated distances
distance_matrix = pd.DataFrame(distances, index=G.nodes, columns=G.nodes)

# Set diagonal values to 0
distance_matrix.values[[range(distance_matrix.shape[0])]*2] = 0

return distance_matrix
result = calculate_distance_matrix(dataset_3)
print(result)

"""Question 2: Unroll Distance Matrix
Create a function unroll_distance_matrix that takes the DataFrame created in Question 1. The resulting DataFrame should have three columns: columns id_start, id_end, and distance.

All the combinations except for same id_start to id_end must be present in the rows with their distance values from the input DataFrame.
"""

import pandas as pd

def unroll_distance_matrix(distance_matrix):
# Get the upper triangular part of the distance matrix
upper_triangle = distance_matrix.where(pd.notna(distance_matrix), 0).values
upper_triangle[np.tril_indices_from(upper_triangle)] = np.nan

# Extract the row and column indices
row_indices, col_indices = np.where(upper_triangle != 0)

# Create a DataFrame with id_start, id_end, and distance columns
unrolled_df = pd.DataFrame({
    'id_start': distance_matrix.index[row_indices],
    'id_end': distance_matrix.columns[col_indices],
    'distance': upper_triangle[row_indices, col_indices]
})

return unrolled_df
unrolled_result = unroll_distance_matrix(result)
print(unrolled_result)

"""Question 3: Finding IDs within Percentage Threshold
Create a function find_ids_within_ten_percentage_threshold that takes the DataFrame created in Question 2 and a reference value from the id_start column as an integer.

Calculate average distance for the reference value given as an input and return a sorted list of values from id_start column which lie within 10% (including ceiling and floor) of the reference value's average.
"""

import pandas as pd

def find_ids_within_ten_percentage_threshold(distance_df, reference_value):
# Filter the DataFrame for the specified reference value
reference_df = distance_df[distance_df['id_start'] == reference_value]

# Calculate the average distance for the reference value
average_distance = reference_df['distance'].mean()

# Calculate the lower and upper bounds within the 10% threshold
lower_bound = average_distance - (average_distance * 0.1)
upper_bound = average_distance + (average_distance * 0.1)

# Filter IDs within the 10% threshold
within_threshold_ids = distance_df[
    (distance_df['id_start'] != reference_value) &
    (distance_df['distance'] >= lower_bound) &
    (distance_df['distance'] <= upper_bound)
]['id_start'].unique()

# Sort the list of IDs
sorted_within_threshold_ids = sorted(within_threshold_ids)

return sorted_within_threshold_ids
reference_value = 1 # Replace with the desired reference value
result = find_ids_within_ten_percentage_threshold(unrolled_result, reference_value)
print(result)

"""Question 4: Calculate Toll Rate
Create a function calculate_toll_rate that takes the DataFrame created in Question 2 as input and calculates toll rates based on vehicle types.

The resulting DataFrame should add 5 columns to the input DataFrame: moto, car, rv, bus, and truck with their respective rate coefficients. The toll rates should be calculated by multiplying the distance with the given rate coefficients for each vehicle type:

0.8 for moto
1.2 for car
1.5 for rv
2.2 for bus
3.6 for truck
"""

import pandas as pd

def calculate_toll_rate(distance_df):
# Define rate coefficients for each vehicle type
rate_coefficients = {
'moto': 0.8,
'car': 1.2,
'rv': 1.5,
'bus': 2.2,
'truck': 3.6
}

# Calculate toll rates for each vehicle type
for vehicle_type, rate in rate_coefficients.items():
    column_name = vehicle_type + '_toll'
    distance_df[column_name] = distance_df['distance'] * rate

return distance_df
result_with_toll_rates = calculate_toll_rate(unrolled_result)
print(result_with_toll_rates)

"""Question 5: Calculate Time-Based Toll Rates
Create a function named calculate_time_based_toll_rates that takes the DataFrame created in Question 3 as input and calculates toll rates for different time intervals within a day.

The resulting DataFrame should have these five columns added to the input: start_day, start_time, end_day, and end_time.

start_day, end_day must be strings with day values (from Monday to Sunday in proper case)
start_time and end_time must be of type datetime.time() with the values from time range given below.
Modify the values of vehicle columns according to the following time ranges:

Weekdays (Monday - Friday):

From 00:00:00 to 10:00:00: Apply a discount factor of 0.8
From 10:00:00 to 18:00:00: Apply a discount factor of 1.2
From 18:00:00 to 23:59:59: Apply a discount factor of 0.8
Weekends (Saturday and Sunday):

Apply a constant discount factor of 0.7 for all times.
For each unique (id_start, id_end) pair, cover a full 24-hour period (from 12:00:00 AM to 11:59:59 PM) and span all 7 days of the week (from Monday to Sunday).
"""

import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta

def calculate_time_based_toll_rates(input_df):
# Convert start and end times to datetime objects
input_df['start_datetime'] = pd.to_datetime(input_df['startDay'] + ' ' + input_df['startTime'])
input_df['end_datetime'] = pd.to_datetime(input_df['endDay'] + ' ' + input_df['endTime'])

# Define time ranges and discount factors
time_ranges_weekdays = [(time(0, 0), time(10, 0), 0.8),
                        (time(10, 0), time(18, 0), 1.2),
                        (time(18, 0), time(23, 59, 59), 0.8)]

time_ranges_weekends = [(time(0, 0), time(23, 59, 59), 0.7)]

# Apply discount factors based on time ranges
for start_time, end_time, discount_factor in time_ranges_weekdays:
    mask = (input_df['start_datetime'].dt.time >= start_time) & (input_df['end_datetime'].dt.time <= end_time) & (input_df['start_datetime'].dt.dayofweek < 5)
    input_df.loc[mask, ['moto', 'car', 'rv', 'bus', 'truck']] *= discount_factor

for start_time, end_time, discount_factor in time_ranges_weekends:
    mask = (input_df['start_datetime'].dt.time >= start_time) & (input_df['end_datetime'].dt.time <= end_time)
    input_df.loc[mask, ['moto', 'car', 'rv', 'bus', 'truck']] *= discount_factor

# Add columns for start day, start time, end day, and end time
input_df['start_day'] = input_df['start_datetime'].dt.strftime('%A')
input_df['start_time'] = input_df['start_datetime'].dt.time
input_df['end_day'] = input_df['end_datetime'].dt.strftime('%A')
input_df['end_time'] = input_df['end_datetime'].dt.time

# Drop temporary columns
input_df = input_df.drop(['start_datetime', 'end_datetime'], axis=1)

return input_df
result_with_time_based_rates = calculate_time_based_toll_rates(unrolled_result)
print(result_with_time_based_rates)