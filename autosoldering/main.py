from pipeline import quality_predict
import pandas as pd

df = pd.read_csv('auto_sample.csv')





pred = quality_predict(df)

print(print(pred))
print('prediction--',pred['OK/NG_pred'])
