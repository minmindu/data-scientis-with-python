
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[1]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[65]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[3]:


def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    data =[]
    with open('university_towns.txt', "r") as file : 
        for line in file  : 
            if (line.strip().endswith('[edit]')): 
                state = line.strip()[:-6]
            else: 
                data.append([state,line.split('(')[0].strip()])

    univ_towns = pd.DataFrame(data,columns = ['State','RegionName']) 
    return univ_towns 

get_list_of_university_towns()


# In[19]:


def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    
    
    # read the excel file
    # data is from row #9
    gdp = pd.read_excel('gdplev.xls', skiprows=7)
    
    # get the target column
    gdp = gdp[['Unnamed: 4', 'Unnamed: 6']]
    gdp.columns = ['quarter','gdpCurrent']
    
    # change data type
    gdp['gdpCurrent'] = pd.to_numeric(gdp['gdpCurrent'])
    
    gdp = gdp.sort_values(['quarter']).loc[212:].reset_index(drop= True)
    
    # to sort out the difference
    # add diff_gdp column
    gdp['diff_gdp'] = gdp.gdpCurrent.diff(+1).apply(lambda x : 1 if x>0 else -1 )
    gdp['diff_gdp'] = gdp.diff_gdp + gdp.diff_gdp.shift(+1)
    
    # start to recession
    res_start_index = gdp[gdp['diff_gdp'] ==-2].index[0]-1
    
    return gdp.iloc[res_start_index].quarter
        

get_recession_start()


# In[25]:


def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    
    # read the excel file
    # data is from row #9
    gdp = pd.read_excel('gdplev.xls', skiprows=7)
    
    # get the target column
    gdp = gdp[['Unnamed: 4', 'Unnamed: 6']]
    gdp.columns = ['quarter','gdpCurrent']
    
    # change data type
    gdp['gdpCurrent'] = pd.to_numeric(gdp['gdpCurrent'])
    
    gdp = gdp.sort_values(['quarter']).loc[212:].reset_index(drop= True)
    
    # to sort out the difference
    # add diff_gdp column
    gdp['diff_gdp'] = gdp.gdpCurrent.diff(+1).apply(lambda x : 1 if x>0 else -1 )
    gdp['diff_gdp'] = gdp.diff_gdp + gdp.diff_gdp.shift(+1)
    
    # about to end recession: diff_dfp = 2 & > get_recession_start() value
    res_end_df = gdp[(gdp['diff_gdp'] ==2) & (gdp.quarter > get_recession_start())]
    
    return res_end_df.iloc[0].quarter
       
get_recession_end()


# In[30]:


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    
    # read the excel file
    # data is from row #9
    gdp = pd.read_excel('gdplev.xls', skiprows=7)
    
    # get the target column
    gdp = gdp[['Unnamed: 4', 'Unnamed: 6']]
    gdp.columns = ['quarter','gdpCurrent']
    # change data type
    gdp['gdpCurrent'] = pd.to_numeric(gdp['gdpCurrent'])
    # set index for quarter
    gdp = gdp.set_index('quarter')
    
    recession_df = gdp.loc[get_recession_start():get_recession_end()]
    
    # get the min of gdpCurrent value and get its index
    min_quarter = recession_df.gdpCurrent.idxmin()
    
    return min_quarter

get_recession_bottom()


# In[66]:


def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    
    # read the csv file
    house = pd.read_csv('City_Zhvi_AllHomes.csv')
    # apply the full state name, NY => New York
    house.State = house.State.apply(lambda x : states.get(x) or x)
    
    # get the data between 2000 - 2016
    ihouse = house.loc[:, '2000-01':'2016-08']
    
    # covert to month
    ihouse.columns = pd.to_datetime(ihouse.columns).to_period(freq="M")
    
    # add the quarter value
    ghouse = ihouse.groupby(ihouse.columns.asfreq("Q"),axis=1).sum()
    
    # attach column
    house = (pd.merge(house.loc[:,"RegionID":"SizeRank"],ghouse,left_index=True,right_index=True,how="inner")
             .set_index(["State","RegionName"]).iloc[:,4:71])
    
    # covert the capital 'Q' to 'q'
    house.columns = [ str(x).lower() for x in house.columns.tolist()  ]
    
    return house

convert_housing_data_to_quarters()


# In[72]:


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    uni_towns = get_list_of_university_towns()
    housing_data = convert_housing_data_to_quarters()
    reccesionStart = get_recession_start()
    reccesionEnd = get_recession_end()
    recessionBottom = get_recession_bottom()
    
    housing_data['compare'] = housing_data[reccesionStart] - housing_data[recessionBottom]
    data = housing_data[['compare']]
    data.reset_index(inplace=True)
    
    # university towns data
    university_towns_data = pd.merge(data, uni_towns, on=['State','RegionName'], how='inner')
        
    university_towns_data['univ'] = True
    university_towns_data.dropna(inplace=True)
    university_towns_data.set_index(['State','RegionName'], inplace = True )

    # non-university data
    non_university_towns_data = pd.merge(data, uni_towns, on=['State','RegionName'], how='outer')
    non_university_towns_data['univ'] = False
    non_university_towns_data.dropna(inplace = True)
    non_university_towns_data.set_index(['State','RegionName'], inplace = True )
    
    # non_university_towns_data.univ.value_counts()
    
    t,p = ttest_ind(university_towns_data.compare, non_university_towns_data.compare)
    
    different = True if p<0.01 else False
    better = "university town" if university_towns_data.compare.mean() < non_university_towns_data.compare.mean() else "non-university town"

    return (different, p, better)    

run_ttest()


# In[ ]:




