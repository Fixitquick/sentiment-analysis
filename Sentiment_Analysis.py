import urllib.request
from bs4 import BeautifulSoup
from textblob import TextBlob
import tweepy
import matplotlib.pyplot as plt
import csv


# Step 1 - Authenticate
consumer_key= 'cyUgsIyEz9uWTQ58E9cKlXDLv'
consumer_secret= 'bpzeVGqEn48mlEdzrnDqxBJjQXzfNmQcsPiJPd8wCpdBPa2NtV'

access_token='817298744-0rjezQ7EcsSyLvlmC5Gl4PDsCDfhwKAaZxwSjIZy'
access_token_secret='lemVAyz76BHAqihG1Wij9U6C7qzfukGk8j7Uipmk1JZ18'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

def getSentiment(api, key):
	public_tweets = api.search(key)
	AvgSentiment = 0
	noOfTweets = len(public_tweets)
	sum1 = 0
	avgRetweets=0
	total_rtw_ct =0
	for tweet in public_tweets:
		text = tweet.text
		rtw_count = tweet.retweet_count
		cleanedtext = ' '.join([word for word in text.split(' ') if len(word) > 0 and word[0] != '@'\
                                and word[0] != '#'and 'http' not in word and word != 'RT'])
		#print(cleanedtext)
		analysis = TextBlob(cleanedtext)
		sentiment = analysis.sentiment.polarity
		sum1 += sentiment
		total_rtw_ct +=rtw_count
		if sentiment == 0:
			#ignore since not a opinion, its a general statement
			noOfTweets -= 1
	if noOfTweets > 0:
		AvgSentiment = sum1/noOfTweets
		avgRetweets=  total_rtw_ct/noOfTweets
	return (AvgSentiment,int(avgRetweets),noOfTweets)

def plotGraph(plotData,color_patt,xlabel,ylabel):
	lists=sorted(plotData.items())
	x,y= zip(*lists)
	plt.title("Loading Analysis Results ...")
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	#plot data
	plt.plot(x,y,color_patt,x,y,'r--')
	#show plot
	plt.show()


#--------------------------------------------------------------------------#

url=urllib.request.urlopen("http://www.google.com/trends/hottrends/atom/feed").read().decode("utf-8")

soup=BeautifulSoup(url, features="xml")
title = []
for element in soup.find_all('title'):
	#print(element.string)
	if element.string == "Hot Trends":
		continue
	title.append(element.string)

views = []
for element in soup.find_all('approx_traffic'):
	view = element.string.replace(',','')
	view = view.strip('+')
	views.append(int(view))

i = 0
trends = dict()
for element in title:
	trends[element] = views[i]
	i += 1

trends = sorted(trends.items(), key=lambda x:x[1])
trends = dict(trends)

coordinates = dict()
flag = 0
plotData_sr={}
plotData_vl={}

sentiment=0
retweet =1
totaltweets=2
with open('sentiment.csv', 'w', newline='\n') as  f:

	writer = csv.writer(f)
	writer.writerow(['Hot Topic','Total Views', 'Sentiment','Retweets','Total tweets'])
	for key, value in trends.items():
		tweet_data = getSentiment(api, key)
		plotData_sr[tweet_data[sentiment]]= tweet_data[retweet]
		plotData_vl[ tweet_data[totaltweets]]= value
		if tweet_data[sentiment] <0:
			sent_data ="Negative"
		else:
			sent_data ="Positive"

		writer.writerow([key,value,sent_data,tweet_data[retweet],tweet_data[totaltweets]])


plotGraph(plotData_sr,'g^','Sentiment','Retweet')
plotGraph(plotData_vl,'bo','Total Tweets','Views')

