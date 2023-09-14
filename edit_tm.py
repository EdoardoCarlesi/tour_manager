import pandas as pd


f_xlsx = 'tour_dates_with_distances.xlsx'
df = pd.read_csv(f_xlsx, encoding='latin1')

print(df.head())

