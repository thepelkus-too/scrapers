# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 15:32:34 2017

@author: Elle
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file. It scrapes people.com
"""
from bs4 import BeautifulSoup
import requests
import string
from datetime import datetime, timedelta
import re
import urllib2
import time
from selenium import webdriver

search_term = "Justin Bieber"
days_ago = 4
# Take out any punctuation marks from name and convert to lowercase
search_term = search_term.translate(None, string.punctuation)
search_term = search_term.lower()

# 
# Format search term for the URL formula
search_term_formatted = search_term.replace(" ", "+")

# For TMZ, update the search formula
#page_link = 'http://eonline.com/search?query=' + search_term_formatted 

page_link = "https://www.buzzfeed.com/search?q=" + search_term_formatted
domain = "https://www.buzzfeed.com"

within_days = 8
#page_link = "https://cnn.com"
#page = requests.get(page_link)
#soup = BeautifulSoup(page.content, 'html.parser')

browser = webdriver.Chrome()
browser.get(page_link)
html = browser.page_source
html = html.encode('UTF8')
browser.close()

soup = BeautifulSoup(html, 'html.parser')

articles = soup.find_all(class_="lede")

days_ago_list = []
article_link_list = []
stories = []
headlines_list = []


# For every article on the page, get the link and the time it was posted at.
for i in range(0,len(articles)):
    article_tags = articles[i]
    child = article_tags.find_all('h2')
    header = child[0].find_all('a')
    
    # URL
    url = domain + header[1]['href']
    url = url.encode('UTF8')
    article_link_list.append(url)
    
    headline = header[1].get_text()
    headline = headline.strip()
    headline = headline.encode('UTF8')
    headlines_list.append(headline)
    
    date_tag = article_tags.find_all(class_="small-meta__item__time-ago")
    date = date_tag[0].get_text()
    date = date.encode('UTF8')
    # Convert buzzfeed date notation to days
    is_min = re.findall('minutes', date)
    is_hours = re.findall('hours', date)
    is_days = re.findall('days', date)
    is_weeks = re.findall('weeks', date)
    is_months = re.findall('months',date)
    is_years = re.findall('years',date)
    num = [int(s) for s in date.split() if s.isdigit()]
    if is_min or is_hours:
        days_ago = 0
    elif is_days:
        days_ago = num[0]
    elif is_weeks:
        days_ago = num[0] * 7
    elif is_months:
        days_ago = num[0] * 30
    elif is_years:
        days_ago = num[0] * 365
    days_ago_list.append(days_ago)
    
    
# Get the articles that are within the given time frame    
is_recent = [x < within_days for x in days_ago_list]
link_indices = [i for i, x in enumerate(is_recent) if x]

for i in range(0, len(link_indices)):
    page_result_link = article_link_list[i]
    page_result = requests.get(page_result_link)
    res_soup = BeautifulSoup(page_result.content, 'html.parser')   
  
    story_tag = res_soup.find_all(class_="subbuzz__description subbuzz__description--standard ")
    if len(story_tag) > 1:
        story_tmp = story_tag[1].get_text()
        story = re.findall('caption":"(.*?)","url"', story_tmp)
        story = ' '.join(story)
        stories.append(story.encode('ascii',errors='ignore'))
    else:
        stories.append('NA')

