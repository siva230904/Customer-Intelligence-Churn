import pandas as pd

#load the dataset

data = pd.read_csv("telecom_churn.csv")
df=pd.DataFrame(data)
#print(df.head())
#print the shape
print(df.shape,df.size)

print()
print(df.columns,len(df.columns))


print(df.dtypes)
print(df.head())