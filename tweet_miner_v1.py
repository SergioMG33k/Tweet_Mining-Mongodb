# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 15:18:18 2021

The script has been developed as a tool to help mine tweets. The script uses a set of statements
from a csv file and will collect tweets based on those statements on twitter. The collected data
will be uploaded to a mongodb database and allows to obtain a local report of the collected data

@author: Sergio
"""

#Imports
import sys
import os
import query_builder_v3_1 as qb
from optparse import OptionParser
import numpy as np
import datetime
import time
import pandas as pd
import json
import tweepy
import os
from tqdm import tqdm
from pymongo import MongoClient
import warnings

warnings.filterwarnings("ignore")

#Option declaration
parser = OptionParser(add_help_option=False)
parser.add_option('-h', '--help', action='store_true', default=False)
parser.add_option('-t', '--time', action='store', type='int', help='number of days ago to search for tweets', default=None)
parser.add_option('-f', '--file', action='store', type='string', help='CSV that contains that contains statements for query generation and information retrieval')
parser.add_option('-l', '--language',action='store', type='string', help='language of statements contained in the csv', default='en')
parser.add_option('--tps',action='store', type='int' , help='maximum tweets per statement to collect', default = None)
parser.add_option('-c', '--max_count', action='store', type='int', help='maximum total amount of tweets to collect', default=None)
parser.add_option('--tw_api_log', action='store', type = 'string',  help='Api_Key/Api_Secret_Key/Access_Token/Access_Token_Secret')
parser.add_option('--mongo_log', action='store', type='string', help='User_name/Password/Database/Collection')
parser.add_option('--report', action='store_true', help='Save locally a .csv file with a report about the number of tweets collected per statement and the total sum.',default=True)
parser.add_option("-v", action="store_true", dest="verbose", default=True)
(options, args) = parser.parse_args()
def print_usage():
    print(r"""
    Information:
        The script has been developed as a tool to help mine tweets. The script uses a set of statements
        from a csv file and will collect tweets based on those statements on twitter. The collected data
        will be uploaded to a mongodb database and allows to obtain a report of the collected data.
        The csv must contain a column with the name hoax_checked, based on the statements contained in
        this column, searches will be carried out on twitter to collect data.
        In the script you need to have access to a developer or academy account to use the api. You 
        have to take into account the request limits in each respective case. It is also worth noting 
        the data recovery time allowed by twitter, for an account academica standard only has access to
        tweets published 7 days ago.
        Once the data is collected, it will be uploaded to mongodb, so it is necessary to enter the 
        credentials for storage in a database.
        The script allows to store locally a .csv file that will contain a report of the number of tweets 
        collected and the date on which the data extraction was performed.
        Note: the generation of queries from the statements is done using the imported script 
        query_builder_v3_1. The code of this script is private and has been developed by the research 
        group Applied Intelligence and Data Analysis of the Polytechnic University of Madrid. If you do 
        not have access to this script, you must modify the code for generating queries where variable 'query' appears.
    Usage:
        python Tweet_mining_v1.py [options]
    Options:
        -t, --time          Number of days ago to search for tweets(0-since today,1-since yesterday...). By default: None(always)
        -f, --file          .csv path that contains statements for query generation and information retrieval
        -c, --maxcount      Maximum total amount of tweets to collect. By default: None 
        -l, --laguage       Language of statements contained in the .csv('en,es,f...). By default: 'en'
        -v                  Verbose.By default: True. Setting as False activates the silent mode.
        --tps               Maximum tweets per statement to collect.By default: None    
        --tw_api_log        Api_Key/Api_Secret_Key/Access_Token/Access_Token_Secret   
        --mongo_log         User_name/Password/Database/Collection   
        --report            Creates a .csv file with the number of tweets collected per statement and their total sum.The file name contains the date when they were collected.'.By  default: False
    
    Rquerements:
        pip install pymongo
        pip install pymongo[srv]
        pip install pymongo[tls]
        pip install tweepy
        pip install tqdm
    Examples:
        python tweet_miner_v1.py -f C:\Users\Sergio\statements.csv \
            --tw_api_log Api_Key/Api_Secret_Key/Access_Token/Access_Token_Secret \
            --mongo_log User_name/Password/Database/Collection \
            --time 7
        Here all the tweets created in the last 7 seven days will be collected
        
        python tweet_miner_v1.py -f C:\Users\Sergio\statements.csv
            --tw_api_log Api_Key/Api_Secret_Key/Access_Token/Access_Token_Secret \
            --mongo_log User_name/Password/Database/Collection \
            --tps 500 \
            --max_count 20000 \
            --time 2
        Here we collect a maximum of 20000 tweets created in the last 2 days, limiting 500 tweets per statement 
        """)
    sys.exit()
    
#Checking arguments
if options.help:
    print_usage()

if not all([options.file, options.tw_api_log, options.mongo_log]):
    print_usage()
    
    
    
#Load statement-file
climatedf= pd.read_csv(os.path.normpath(options.file))
statements= [ statement for statement in climatedf['Hoax-Checked']]


#Connect to twitter api
Api_Key, Api_Secret_Key, Access_Token, Access_Token_Secret = options.tw_api_log.split(sep='/')
auth = tweepy.OAuthHandler(Api_Key, Api_Secret_Key)
auth.set_access_token(Access_Token, Access_Token_Secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

#Connect to mongodb Database
user_mongo, password, database, collection = options.mongo_log.split(sep='/')
client = MongoClient(f"mongodb+srv://{user_mongo}:{password}@cluster0.yho6n.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client[database]
collection = db[collection]

#Functions
def extract_data(statement, tweets_count=None):
    """
    Extract data using twitter api from statement
    
    Parameters
    ----------
    Statement : string
        Statement to search by query
    tweets_count : integer
    Returns
    -------
    Data : list of dictionaries
        Each document collected through the twitter api saved in a list
    Query : string
        Query generated to search on twitter
    Count : integer
        Number of tweets collected(It can coincide with the tweet_counts parameter or be less depending on the number of available tweets )
    """
    data =[]
    query = qb.get_kw_comb_v2(statement_text=statement, #building query with private script
                                            language_code=options.language, 
                                            lemmatized=False, 
                                            level = 1,
                                            top_n = 7, 
                                            diversity = 0.2, 
                                            max_query_len = 1024
                                            )
    for tweet  in tweepy.Cursor(api.search_tweets, q=query, tweet_mode="extended").items(): 
        if len(data) == tweets_count: #checking if tweets collected exeed the argument tweets_count(option tps), if that the case stop collecting
            break
        created_at = tweet.created_at
        tweet = tweet._json
        tweet['Hoax'] = statement
        tweet['Query'] = query
        
        #we filter tweets by date taking into account option --time
        if options.time == None:
            data.append(tweet)
        else:
            since  = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(options.time) #conversion of the option --time in date format
            if since.date() <= created_at.date():
                data.append(tweet)
        
    count=len(data) #Number of tweets that the function will return

    return data, query, count

#Tweet mining
tweets_collected = []
report = [] #we save a list of dictionaries, each dictionary is a report with information about one statement
if options.verbose:
    print('Collecting data from twitter...')
for idx,statement in enumerate(tqdm(statements)):
    try:
        data, query, count = extract_data(statement, tweets_count=options.tps) #data extraction where argument tps(tweets per statement) is used
        tweets_collected.extend(data)
        if (options.max_count != None) and (len(tweets_collected) > options.max_count): # Checking if total amount of tweets collected exceeds the argument 'maxcount'
            tweets_collected = tweets_collected[:options.max_count]
            break
        statement_report = {}
        statement_report['index'] = idx
        statement_report['statement'] = statement
        statement_report['tweet count'] = count
        report.append(statement_report) 
    except Exception:
        pass
df_report = pd.DataFrame(report) #Report is saved in a dataframe

#Upload tweets mined to mongo database
if options.verbose:
    print('Uploading data to mongoDB...')
    
for tweet in tweets_collected:
    collection.update_one({'id' : tweet['id']},{"$set": tweet}, upsert = True)

#Save report locally
if options.report:
    if not os.path.isdir('tweet_miner_reports/'):
        os.mkdir('tweet_miner_reports')
    df_report = df_report.append({'statement':'Tweets total count','tweet_count':len(tweets_collected)},ignore_index=True)
    df_report = df_report.append({'statement':'Date','tweet_count':f'{datetime.datetime.now()}'},ignore_index=True)
    df_report.to_csv(f'tweet_miner_reports/tweet_miner_report_{datetime.datetime.now().date()}_{datetime.datetime.now().strftime("%Hh%Mm%Ss")}_.csv')
if options.verbose:
    print(f'A total of {len(tweets_collected)} tweets were collected and uploaded to "{database}" database successfully at {datetime.datetime.now().hour}:{datetime.datetime.now().minute} on {datetime.datetime.now().date()}')
    if options.report:
        print('A report was saved locally')


    
    
