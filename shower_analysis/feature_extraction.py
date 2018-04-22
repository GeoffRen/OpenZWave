from pandas import read_csv

CSV_NAME = 'geoff_on_off_testing'
QUERY_INTERVAL = 20000000000 # 20 instead of 15 to compensate for lag


def get_humidity_changes(data, time_steps):
    humidity_changes = [0]*time_steps
    for i in range(time_steps, len(data)):
        if data.iloc[i, 1] - data.iloc[i - time_steps, 1] > QUERY_INTERVAL*time_steps:
            print("Difference in time between {} and {} is {} minutes"
                  .format(i, i - time_steps, (data.iloc[i, 1] - data.iloc[i - time_steps, 1]) / 60000000000))
            humidity_changes.append(0)
        else:
            humidity_changes.append(data.iloc[i, 2] - data.iloc[i - time_steps, 2])
    print()
    return humidity_changes


data = read_csv('original_csvs/{}_orig.csv'.format(CSV_NAME))

# Use previous label as a feature.
type_vals = data['type_val'].tolist()
type_vals.pop()
type_vals.insert(0, 0)
data["prev_type_val"] = type_vals

# Use change in humidity levels from previous data points as features.
data["humidity_change_1"] = get_humidity_changes(data, 1)
data["humidity_change_2"] = get_humidity_changes(data, 2)
data["humidity_change_3"] = get_humidity_changes(data, 3)
data["humidity_change_4"] = get_humidity_changes(data, 4)
data["humidity_change_5"] = get_humidity_changes(data, 5)
data["humidity_change_6"] = get_humidity_changes(data, 6)
data["humidity_change_7"] = get_humidity_changes(data, 7)
data["humidity_change_8"] = get_humidity_changes(data, 8)
data["humidity_change_9"] = get_humidity_changes(data, 9)

# Saves data as a csv.
print("~~~Saving~~~\n")
data.to_csv('{}.csv'.format(CSV_NAME), index=False)

print("Done!")
