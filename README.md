# Tweet_Miner-Mongodb
The tweet_miner tool has been created to help mine twitter data such as hoaxes and fake news about covid and climate change in my Master Thesis. 
The disinformation data was used to train and fine-tune artificial intelligence transformer models as well as to do analysis of data.
In this repository there is also a folder called DATA with a .csv file that contains checked hoaxes collected from fact-checkers. These hoaxes will be used to mine related tweets on twitter and generate a NoSQL database with mongodb.
Feel free to use my tool and make modifications.

    Information:
        The script uses a set of statements
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
        python tweet_miner_v1.py -f C:\Users\Sergio\statements.csv
        --tw_api_log Api_Key/Api_Secret_Key/Access_Token/Access_Token_Secret 
        --mongo_log User_name/Password/Database/Collection
        --time 7
        Here all the tweets created in the last 7 seven days will be collected
        
        python tweet_miner_v1.py -f C:\Users\Sergio\statements.csv
        --tw_api_log Api_Key/Api_Secret_Key/Access_Token/Access_Token_Secret 
        --mongo_log User_name/Password/Database/Collection
        --tps 10000
        --max_count 70000
        --time 2
        Here we collect a maximum of 70000 tweets created in the last 2 days, limiting 10000 tweets per statement 
        
