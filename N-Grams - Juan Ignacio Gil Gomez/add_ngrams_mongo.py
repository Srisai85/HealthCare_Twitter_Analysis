##########################################################
#
# Author: Juan Ignacio Gil
# email: juan.ignacio.gil.gomez@gmail.com
# date: July 2014
#
##########################################################

"""
    add_ngrams_mongo.py
    
    Go through the tweets in the database and add the n-grams as embedded objects in each tweet object
    
    Execute as:
    
        add_ngrams_mongo.py n
    
    with n as maximum rank of the n-grams
"""

from nltk.util import ngrams
from pymongo import MongoClient
import sys
import re


###########################################################################################

def loop_database(n):

    """
        Go through the tweets in the database
    """

    #Database
    client = MongoClient()
    db = client['HealthCare_Twitter_Analysis']
    
    col = db.tweets
    docs=col.find({'n-grams.0':{'$exists': False}}).batch_size(50)
    #docs=col.find().batch_size(50)
    total=docs.count()
    print repr(total)+' documents to include n-grams'
    nt=0

    #Iterate over all elements in the collection without n-grams field
    for tweet in docs:
        add_ngrams_tweet(tweet,col,n)
        nt+=1

        #Just for let you know that it's working
        if nt%1000==0:
            print tweet['content']+' ... '+repr(nt*100/total)+'% done...'

###########################################################################################

def update_all_tweets_in_database(n):
    
    """
        Go through the tweets in the database
        """
    
    #Database
    client = MongoClient()
    db = client['HealthCare_Twitter_Analysis']
    
    col = db.tweets
    docs=col.find().batch_size(50)
    #docs=col.find().batch_size(50)
    total=docs.count()
    print repr(total)+' documents to include n-grams'
    nt=0
    
    #Iterate over all elements in the collection without n-grams field
    for tweet in docs:
        add_ngrams_tweet(tweet,col,n)
        nt+=1
        
        #Just for let you know that it's working
        if nt%1000==0:
            print tweet['content']+' ... '+repr(nt*100/total)+'% done...'


###########################################################################################

def add_ngrams_tweet(tweet,col,n):

    """
        Calculate the ngrams for a single tweet and add them as a single object
    """

    list_of_ngrams=[]
    #Delete special characters, convert to lowercase, and split into words
    words=re.sub('[^a-zA-Z0-9\@]', ' ', tweet['content']).lower().split()

    for rank in range(1,n+1):
        #Generate n-grams
        for gram in ngrams(words, rank):
            #We don't want links in our n-grams
            if all([not w.startswith("http") for w in gram]):
                list_of_ngrams.append({'rank':rank,'text':gram})

    tweet['n-grams']=list_of_ngrams

    #Update in the database
    col.update({'_id':tweet['_id']}, {"$set": tweet}, upsert=False)




###########################################################################################

if __name__ == '__main__':
    
    loop_database(int(sys.argv[1]))
