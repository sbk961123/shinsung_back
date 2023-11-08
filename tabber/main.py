from pipeline import quality_predict
import pandas as pd

df = pd.read_excel('test_data2.xlsx')

pred = quality_predict(df)

print(pred,'predpred')