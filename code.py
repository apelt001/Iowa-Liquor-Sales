import pandas as pd
import pickle
import matplotlib.pyplot as plt


# Since our dataset has ~19M rows, let's start by loading just the first 100 rows and see what columns we are going to use:

# Note: I will also load a population by zip code table.
zips = pd.read_csv("Pop_by_County.txt",sep='\t')

# For the date column, I will use a date parsing function to ensure the proper data type will be loaded
def date_parser(x):
    X=[int(i) for i in str(x).split('/')]
    m,d,y = X[0],X[1],X[2]
    return pd.datetime(year=y,day=d,month=m)

df = pd.read_csv("Iowa_Liquor_Sales.csv",parse_dates=['Date'],date_parser=date_parser,nrows=100)
print(zip(range(len(df.columns)),df.columns.tolist()))

# Ok, so there are 24 columns, but some of them can be inferred from the rest. For example, 
# the 'Volume Sold (Liters)' column is just "Bottles Sold" multiplied by "Bottle Volume (mL)"
# Clearly then, we shouldn't load the whole dataset 


z=pickle.load(open("Pop_by_County.p","rb"))


# Let's find out what Categories of Liquor Sales there are: 
C = pd.read_csv("Iowa_Liquor_Sales.csv",usecols=[10,11])
C=C.dropna().drop_duplicates().reset_index(drop=True)


# We notice that the category codes are neatly grouped. If the code starts with "103", for example, then it is a Vodka. We use modular arithmetic to slice the frame:
lcodes={}

lcodes[101] = 'Whiskey'
lcodes[102] = 'Tequila'
lcodes[103] = 'Vodka'
lcodes[104] = 'Gin'
lcodes[105] = 'Brandies'
lcodes[106] = 'Rum'
lcodes[107] = "Cocktails"
lcodes[108] = "Liquers"
lcodes[109] = "Distilled Spirits"
lcodes[110] = ""
lcodes[150] = "High Proof Beer"
lcodes[170] = "Temporary and Specialty Packages"
lcodes[190] = "Special Order Items"

Vodka=C[C['Category'].apply(lambda x: x//10000)==103]
Whiskies=C[C['Category'].apply(lambda x: x//10000)==101]

# Let's group the liquors by liquor type, and see how they sell
df['Liquor Type'] = df['Category'].apply(lambda x: x//10000)
bytype=df.groupby("Liquor Type").size()

d = bytype.loc[[101,103,106,108]]
y = [xx/1000. for xx in d]
plt.figure()
plt.bar(x,y)
plt.title("Distribution of Liquor Sold")
labels = [lcodes[i] for i in [101,103,106,108]]
plt.xticks(x,labels)
plt.ylabel("Number of Sales (in Thousands)")
plt.savefig("Dis_Liquor.png")
plt.close()





# Even more, '1032' is imported vodka, '1031' is American vodka:
# We notice the fourth digit is 1 if its imported, 2 if its domestic, and 0 if its a special order item

df = pd.read_csv("Iowa_Liquor_Sales.csv",usecols=[1,6,10,22],parse_dates=['Date'],date_parser=date_parser)
df=df.dropna()
df['is_imported'] = (df.Category.apply(lambda x: str(x)[3] == '2')).astype(int)


print(df['is_imported'].mean())
# We see that about 42% of sales are of imported liquor, and this is consistent throughout the years:

print(df.groupby(df.Date.dt.year)['is_imported'].mean())









# Now let's look at the location of the stores


def fix_lat(h):
    H=h.split("(")[1].split(" ")[0]
    return float(H)
def fix_lon(h):
    H=h.split(")")[0].split(" ")[-1]
    return float(H)


store_locs = pd.read_csv("Iowa_Liquor_Sales.csv",usecols = [2,7])
store_locs=store_locs.dropna()
L=store_locs['Store Location']
lat = L.apply(fix_lat)
lon = L.apply(fix_lon)
H=pd.DataFrame(store_locs['Store Number'])
H['lat'] = lat
H['lon']=lon
H=H.drop_duplicates()
# Remove the outliers
A = H['lon']<= 44
B = H['lon']>40
C=H['lat']<-80
H=H[A&B&C]




store_locs=store_locs.drop_duplicates()
# This will help fix the stupid double counting of certain store_locs
store_locs = store_locs.groupby("Store Number").first()









# Draw the State-Boundary Lines

import json
j=json.load(open("gz_2010_us_040_00_500k.json","rb"))
B=j['features'][33]['geometry']['coordinates'][0]
x=[i[0] for i in B]
y=[i[1] for i in B]



plt.figure()plt.title("Liquor Stores in Iowa")

# Plot a point for each Store in the dataset
plt.scatter(H['lat'],H['lon'],s=.01)

plt.plot(x,y)


# Plot the names of the four major cities
City_Coords = pd.read_csv("iowa_city_coords.txt",sep='\t')
def K(s):
    S=s.split(" / ")
    return (float(S[0]),float(S[1]))
l=City_Coords['Latitude/Longitude'].apply(K).tolist()
l0 = [k[0] for k in l]
l1 = [k[1] for k in l]
n=[name.strip() for name in City_Coords['Name'].tolist()]


plt.scatter(l1[:4],l0[:4],color = 'orange', s=10)
for i,txt in enumerate(n[:4]):
    plt.annotate(txt, (l1[i],l0[i]))


plt.savefig("StoreMap.png")


plt.close()








# Plot a graph of the stores ranked by total sales in volume of liquor sold. The x pltis is the rank, y is the volume. What type of distribution does this follow?


S = pd.read_csv("Iowa_Liquor_Sales.csv",usecols = [2,12,22])

#StoresByVolume = S.groupby("Store Number")['Volume Sold (Liters)'].sum().sort_values(ascending=False)

VendorsByVolume = S.groupby("Vendor Number")['Volume Sold (Liters)'].sum().sort_values(ascending=False)
# Remove the smallest Vendors
VV=VendorsByVolume[VendorsByVolume>10000]

plt.figure()
plt.title("Vendors ranked by Volume of total liquor sold")
plt.xlabel("Rank")
plt.ylabel("Volume sold (in Liters)")
plt.plot(range(len(VV)),VV)
plt.savefig("Vendors_by_rank.png")
plt.close()


# Make a list of all the stores and their store names
#Stores = pd.read_csv("Iowa_Liquor_Sales.csv",usecols = [2,3])
#Stores = Stores.dropna()
#stores=Stores.groupby("Store Number").first()

#Vendors = pd.read_csv("Iowa_Liquor_Sales.csv",usecols = [12,13])
#Vendors = Vendors.dropna()
#vendors=Vendors.groupby("Vendor Number").first()


#VV.iloc[:13]
#vendors.loc[VendorsByVolume.index[:10].tolist()]

#stores=Stores.groupby("Store Number").first()
