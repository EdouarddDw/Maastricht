#import data from nba.cvs and from survey_results_public.csv
import pandas as pd
import numpy as np

nba = pd.read_csv('nba.csv')
survey = pd.read_csv('survey_results_public.csv')


#print nba
print(nba)

#find players based on thier name
print(nba[nba['Name'] == 'LeBron James'])

