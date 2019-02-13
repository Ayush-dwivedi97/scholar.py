from flask import Flask
from newsapi import NewsApiClient
import json
import logging
import requests
import twitter
import scholar 
import pandas as pd
import whois
#github app keys
client_id="daca93d357436f2419a2"
client_secret_id="19f8de8557554e5d9191df976ea5d56be5b93bc8"
app = Flask(__name__)
#to find projects and score of user in behance
def behance_search(name,x):
    headers = {
            'cache-control': "no-cache"
            }
    client_id='Ot8sKC1S9u85XHb8Tm1dliBXX1XE36vS'
    user_id=name
    user_url="https://api.behance.net/v2/users/{}?client_id={}".format(user_id,client_id)
    response = requests.request("GET", user_url, headers=headers)
    user_data=json.loads(response.text)
    user_data=user_data['user']
    user_url="https://api.behance.net/v2/users/{}/projects?client_id={}".format(user_id,client_id)
    response = requests.request("GET", user_url, headers=headers)
    user_project=json.loads(response.text)
    user_project=user_project['projects']
    stats=user_data['stats']
    score=(0.1*stats['appreciations'])+(0.01*stats['comments'])+(0.1*stats['followers'])+(0.001*stats['views'])
    score=score/1000
    report={
            "Name":user_data['display_name'],
            "Score":score
            }
    result=dict()
    result=report
    count=0
    while count<int(x):
        project=user_project[count]
        project_report={
                    "Title":project['name'],
                    "Stats":project['stats']
                    }
        result[str(count)]=project_report
        count=count+1
    return result


#to find the domain ownership
def domain_ownership(name):
    domain =whois.query(name)
    details=domain.__dict__
    del details['creation_date']
    del details['expiration_date']
    del details['last_updated']
    del details['name_servers']
    return details
#to find latest x media articles about user
def media_search(user,x):
    newsapi = NewsApiClient(api_key='7346992c0c8f48a5a8c794a9597c9b7d')
    all_articles_user = newsapi.get_everything(q=user,
                                      language='en',
                                      sort_by='relevancy',
                                      )
    article_data=all_articles_user['articles']
    articles=dict()
    count=0
    x=int(x)
    for count in range(x):
    	if count<len(article_data):
	     articles[str(count)]=article_data[count]
    return articles

#to find the patent search of any author
def patent_search(query):
    try:
        query_list = query.split(' ')
    except:
        query_list = query
    query=query.lower()
    if len(query_list) == 1:
        url = 'https://patents.google.com/xhr/query?url=q%3D' + query + '%26exp=&download=true'
        
    else:
        url_temp = 'https://patents.google.com/xhr/query?url=q%3D' + query_list[0]
        for i in range(1, len(query_list)):
            url_append = '%2B' + query_list[i]
            url_temp += url_append
            url = url_temp +  '%26exp=&download=true'
    data = pd.read_csv(url, sep = ',', skiprows = 1)
    data=data.drop(columns=['filing/creation date','priority date','grant date','representative figure link','id'])
    data['inventor/author']=data['inventor/author'].str.lower()
    data=data[data['inventor/author'].str.contains(query,na=False)]
    data=data.reset_index().to_json(orient='records')
    return data
#to find paper published by the user
def google_scholar(username):
    print("google-scholar api called, username is ",username)
    querier = scholar.ScholarQuerier()
    settings = scholar.ScholarSettings()
    querier.apply_settings(settings)
    query = scholar.SearchScholarQuery()
    query.set_author(username)
    query.set_num_page_results(19)
    querier.send_query(query)
    reports= querier.articles[:]
    count=0
    result=dict()
    while count<len(reports):
        report=reports[count]
        user_report={
                "title":report['title'],
                "citation":report['num_citations'],
                "year":report['year']
                }
        result[str(count)]=user_report
        count=count+1
    print("google-scholar api called, result  is calculated successfully")
    return result
#to find the github id score
def github_score(username):    
    logging.info('github-score api called, username is %s',username)
    headers = {
            'cache-control': "no-cache"
            }
    user_url="https://api.github.com/users/{}?client_id={}&client_secret={}".format(username,client_id,client_secret_id)
    response = requests.request("GET", user_url, headers=headers)
    user_data=json.loads(response.text)
    followers=user_data['followers']
    repositories=user_data['public_repos']
    repos=[]
    pages=(user_data['public_repos']/100)
    if user_data['public_repos']%100!=0:
        pages=(int)(pages+1)
    while pages>0:
        repos_url = "https://api.github.com/users/{}/repos?per_page=100&page={}&client_id={}&client_secret={}".format(username,pages,client_id,client_secret_id)
        pages=pages-1
        response = requests.request("GET", repos_url, headers=headers)
        repos_info=json.loads(response.text) 
        repos=repos+repos_info
    count=0
    sum_stars=0
    sum_forks=0
    score=0
    while count<len(repos):
        repo=repos[count]
        sum_stars=sum_stars+repo['stargazers_count']
        sum_forks=sum_forks+repo['forks']
        count=count+1
    score=(sum_stars*10)+(sum_forks*10)+(followers*5)+(repositories)
    score=score/100
    logging.info('github-score api called, result  is calculated successfully')
    return score
#get last x tweets of the user
def tweets(user,x):
    logging.info('twitter api called, username is %s',user)
    api = twitter.Api()
    #private credentials to use OAuth
    api = twitter.Api(consumer_key='oi90IdOkPhTjZUOZ7sBW065oM',
                      consumer_secret='ga9Oy8dKafVEHdZsXkW6qEatb3H2mf8CVPf0al78z0EFFIAiRg',
                      access_token_key='1089823192934363136-G82OUgsMekc32gw8suov7beaqKwCrR',
                      access_token_secret='j7G2KKJ9j2pbN6PEtHISRq3QzORyYjj0vmRX3t7YO4vds',
                      tweet_mode='extended')
    
    statuses = api.GetUserTimeline(screen_name=user,count=x)
    status=[s.full_text for s in statuses]
    logging.info('twitter api called, result  is calculated successfully')
    return status
@app.route('/behance/<user>/<x>',methods = ['POST', 'GET'])
def behance(user,x):
     try:
          result=behance_search(user,x)
          result=json.dumps(result)
          return result
     except:
         return "ERROR:wrong input"

@app.route('/domain/<user>',methods = ['POST', 'GET'])
def domain(user):
      try:
          result=domain_ownership(user)
          result=json.dumps(result)
          return result
      except:
          return "ERROR:wrong input"

@app.route('/media/<user>/<x>',methods = ['POST', 'GET'])
def media(user,x):
     try:
          result=media_search(user,x)
          result=json.dumps(result)
          return result
     except:
         return "ERROR:wrong input"

@app.route('/patent/<user>',methods = ['POST', 'GET'])
def patent(user):
      try:
          result=patent_search(user)
          return result
      except:
          return "ERROR:wrong input"

@app.route('/paper/<user>',methods = ['POST', 'GET'])
def paper(user):
      try:
          print("usr is:%s",user)
          result=google_scholar(user)
          result=json.dumps(result)
          return result
      except:
          return "ERROR:wrong input"

@app.route('/github/<user>',methods = ['POST', 'GET'])
def github(user):
      try:
          result=github_score(user)
          user_score={
                  "Github_User_id":user,
                  "Score":result
                  }
          user_score=json.dumps(user_score)
          return user_score
      except:
          return "ERROR:wrong input"
@app.route('/tweet/<user>/<x>',methods = ['POST', 'GET'])
def tweet(user,x):
    try:
        result=tweets(user,x)
        user_tweets={
                "twitter_username":user,
                "tweets":result
                }
        user_tweets=json.dumps(user_tweets,ensure_ascii=False)
        return user_tweets
    except:
        return "ERROR:wrong input"
@app.route('/health',methods = ['GET'])
def health():
    return "Running successfully!"

if __name__ == '__main__':
    app.run(debug = True,host='0.0.0.0')

