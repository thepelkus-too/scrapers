# -*- coding: utf-8 -*-
"""
Created on Sun Aug 27 20:23:50 2017

This defines the functions to be used in a module so that *all* the tabloid scrapers
we're currently using can be called at once.

@author: Elle
"""


### Get the search term from the user ###
def get_search_term_from_user():
    search_term = input('Enter search term:\n')
    search_term_string = search_term.replace(' ', '+')
    return search_term_string


### Get the number of days ago from the user ###
def get_days_ago_from_user():
    return input('How many days ago?\n')


### Get file destination from the user ###
def get_destination_from_user():
    return input('Choose save name:\n')


### Write results to file ###
def write_results_to_file(results, basename):
    outfilename = "Results/%s.txt" % basename
    if len(results) >= 1:
        for item in range(0, len(results)):
            # Find out what our file number should be
            file_num = item
            outfile = open(outfilename, 'a', encoding='utf-8')
            outfile.write(results[item])
            outfile.close()


#### Scrape E! Online #####


def EScraper(search_term, days_ago):
    from bs4 import BeautifulSoup
    import requests
    import string
    import re
    from selenium import webdriver
    from dateutil import parser
    from datetime import datetime, timedelta
    import time
    import os
    from sys import platform

    # Take out any punctuation marks from name and convert to lowercase
    search_term = search_term.translate(
        str.maketrans('', '', string.punctuation))
    search_term = search_term.lower()

    #
    # Format search term for the URL formula
    search_term_formatted = search_term.replace(" ", "+")

    # Pull the HTML for the page using Selenium--->bs4 pipeline
    page_link = "http://eonline.com/search?query=" + search_term_formatted

    # if platform == "linux" or platform == "linux2":
    #     cwd = os.getcwd()
    #     browser = webdriver.Chrome(cwd + '/chromedriver')
    # elif platform == "win32" or platform == "win64":
    #     browser = webdriver.Chrome()
    # else:
    #     cwd = os.getcwd()
    #     browser = webdriver.Chrome(cwd + '/chromedriver')
    browser = webdriver.PhantomJS()

    browser.get(page_link)
    html = browser.page_source
    browser.close()
    browser.quit()
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all(class_="result")

    #### Initialize the vectors for storing results
    timestamp = []
    article_link_list = []
    headlines_list = []
    fetched_stories = []
    fetched_headlines = []
    all_text = []

    # Loop over every search result the query pulls
    for i in range(0, len(articles)):
        this_article = articles[i]
        headline_tag = this_article.find_all(class_="result-body")
        date_tag = this_article.find_all(class_="News")
        link_tag = this_article.find_all("a")

        # Update headline list
        headline = headline_tag[0].get_text()
        headlines_list.append(headline.encode('utf-8'))

        # Get the link
        link = link_tag[0]['href']
        article_link_list.append(link.encode('utf-8'))

        # Get the date stamp in the correct format
        date_full = date_tag[1].get_text()
        date_full = date_full.encode('utf-8')  #encode into utf-8 string
        date_short = re.findall(' .*$', date_full.decode('utf-8'))
        timestamp.append(parser.parse(date_short[0]))

    ##### Of the results we got, how many are recent enough?
    is_recent = [
        datetime.today() - timedelta(days=days_ago) < x for x in timestamp
    ]
    link_indices = [i for i, x in enumerate(is_recent) if x]

    # Loop over the recent results
    for i in range(0, len(link_indices)):
        page_result_link = article_link_list[link_indices[i]]
        page_result = requests.get(page_result_link)
        res_soup = BeautifulSoup(page_result.content, 'html.parser')
        story_tag = res_soup.find_all(
            class_=
            "post-content text-block clearfix post-content--groupedn-txt ")
        story = ""
        for j in range(0, len(story_tag)):
            story_tmp = story_tag[j].get_text()
            story_tmp = story_tmp
            story += story_tmp

        # append to lists!
        title = headlines_list[link_indices[i]].decode('utf-8')

        story = re.sub(r'\.article_pinterest.*?\}', ' ', story)
        story = re.sub(r'var.*?\;', ' ', story)
        story = re.sub(r'function.*?\}\)\;', ' ', story)

        fetched_headlines.append(title)
        fetched_stories.append(story)

        all_text.append(story)
        all_text.append(title)

    return all_text


######## Define our scraper for Radar Online
def RadarScraper(search_term, days_ago):
    from bs4 import BeautifulSoup
    import requests
    import string
    from datetime import datetime, timedelta
    import re
    import time
    from dateutil import parser
    import os

    # Take out any punctuation marks from name and convert to lowercase
    search_term = search_term.translate(
        str.maketrans('', '', string.punctuation))
    search_term = search_term.lower()

    # Format search term for the URL formula
    search_term_formatted = search_term.replace(" ", "+")

    page_link = "http://radaronline.com/search/?search=" + search_term_formatted
    page = requests.get(page_link)
    soup = BeautifulSoup(page.content, 'html.parser')

    timestamp = []
    article_link_list = []
    headlines = []
    fetched_stories = []
    fetched_headlines = []
    all_text = []

    articles = soup.find_all('article')

    # For every article on the page, get the link and the time it was posted at.
    for i in range(0, len(articles)):
        this_article = articles[i]

        headline_tag = this_article.find_all(class_="promo-title")
        date_tag = this_article.find_all(class_="posted-date")
        link_tag = this_article.find_all("a")

        # Update headline list
        headline = headline_tag[0].get_text()
        headlines.append(headline)

        # Get the link
        link = link_tag[0]['href']
        article_link_list.append(link)

        # Get the date stamp in the correct format
        date_full = date_tag[0].get_text()
        date_full = date_full.encode('utf-8')  #encode into utf-8 string
        date_short = re.findall('(?<=Posted )(.*)(?= @)',
                                date_full.decode('utf-8'))
        timestamp.append(parser.parse(date_short[0]))

    # Which articles were posted within N days?
    is_recent = [
        datetime.today() - timedelta(days=days_ago) < x for x in timestamp
    ]
    link_indices = [i for i, x in enumerate(is_recent) if x]

    for i in range(0, len(link_indices)):
        page_result_link = article_link_list[link_indices[i]]
        page_result = requests.get(page_result_link)
        res_soup = BeautifulSoup(page_result.content, 'html.parser')
        story_tag = res_soup.find_all(class_="entry")
        if story_tag and not story_tag[0].find_all(
                class_="fs-gallery_body"
        ):  # Gracefully handle in case nothing comes up
            story = story_tag[0].get_text()

            title = headlines[link_indices[i]]

            fetched_headlines.append(title)

            fetched_stories.append(story)

            all_text.append(title)
            all_text.append(story)

    return all_text


#################### Perez scraper ###########################################
def PerezScraper(search_term, days_ago):
    from bs4 import BeautifulSoup
    import requests
    import string
    from selenium import webdriver
    from dateutil import parser
    from datetime import datetime, timedelta
    import time
    import re
    from sys import platform
    import os

    # Take out any punctuation marks from name and convert to lowercase
    search_term = search_term.translate(
        str.maketrans('', '', string.punctuation))
    search_term = search_term.lower()

    # Format search term for the URL formula
    search_term_formatted = search_term.replace(" ", "+")

    page_link = "http://perezhilton.com/search/" + search_term_formatted

    # if platform == "linux" or platform == "linux2":
    #     cwd = os.getcwd()
    #     browser = webdriver.Chrome(cwd + '/chromedriver')
    # elif platform == "win32" or platform == "win64":
    #     browser = webdriver.Chrome()
    # else:
    #     cwd = os.getcwd()
    #     browser = webdriver.Chrome(cwd + '/chromedriver')
    browser = webdriver.PhantomJS()

    browser.get(page_link)
    html = browser.page_source
    browser.close()
    browser.quit()

    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all(class_="post")  # This will get some junk, too.

    #### Initialize the vectors for storing results
    timestamp = []
    article_link_list = []
    headlines_list = []
    fetched_stories = []
    fetched_headlines = []
    all_text = []

    for i in range(1, len(articles)):
        child = articles[i].find_all("a")

        # If it really is a search result- as in, child isn't empty-
        if child:
            headline = child[0].get_text()
            headlines_list.append(headline.encode('utf-8', errors='ignore'))
            link = child[0]['href']
            article_link_list.append(link.encode('utf-8', errors='ignore'))
            date = re.findall('[0-9]{4}-[0-9]{2}-[0-9]{2}', link)
            timestamp.append(
                parser.parse(date[0].encode('utf-8', errors='ignore')))

    ##### Of the results we got, how many are recent enough?
    is_recent = [
        datetime.today() - timedelta(days=days_ago) < x for x in timestamp
    ]
    link_indices = [i for i, x in enumerate(is_recent) if x]

    # Loop over the recent results. May have to introduce pagination if the last date
    # presented is too recent, since Perez only shows six articles at a time.
    for i in range(0, len(link_indices)):
        page_result_link = article_link_list[link_indices[i]]
        page_result = requests.get(page_result_link)
        res_soup = BeautifulSoup(page_result.content, 'html.parser')
        story_tag = res_soup.find_all(class_="entry ")
        story_tmp = story_tag[0].get_text()
        story = story_tmp.split("\nTags:")[0]

        fetched_stories.append(story)
        fetched_headlines.append(
            headlines_list[link_indices[i]].decode('utf-8'))
        all_text.append(story)
        all_text.append(headlines_list[link_indices[i]].decode('utf-8'))

    return all_text


###################### Scrape People #########################################
def PeopleScraper(search_term, days_ago):
    from bs4 import BeautifulSoup
    import requests
    import string
    from datetime import datetime, timedelta
    import re
    import time
    import os

    # Take out any punctuation marks from name and convert to lowercase
    search_term = search_term.translate(
        str.maketrans('', '', string.punctuation))
    search_term = search_term.lower()

    #
    # Format search term for the URL formula
    search_term_formatted = search_term.replace(" ", "+")

    # For TMZ, update the search formula
    #page_link = 'http://eonline.com/search?query=' + search_term_formatted

    page_link = "http://people.com/?s=" + search_term_formatted
    page = requests.get(page_link)
    soup = BeautifulSoup(page.content, 'html.parser')

    timestamp = []
    article_link = []
    fetched_stories = []
    fetched_headlines = []
    all_text = []

    articles = soup.find_all('article')

    # For every article on the page, get the link and the time it was posted at.
    for i in range(0, len(articles)):
        this_article = articles[i]
        article_tags = this_article.contents[1]

        time_children = article_tags.find_all(
            class_="article-header__timestamp")
        if not time_children:
            timestamp.append(datetime.strptime('January 1 1900', "%B %d %Y"))
        else:
            timestamp_tmp = time_children[0].get_text()
            timestamp_stripped = re.findall(' on (.*?) at', timestamp_tmp)
            if timestamp_stripped:
                timestamp_stripped = timestamp_stripped[0]
                timestamp_stripped = timestamp_stripped.encode(
                    'utf-8', errors='ignore')
                timestamp_stripped = timestamp_stripped.translate(
                    None, string.punctuation.encode('utf-8'))
                timestamp.append(
                    datetime.strptime(
                        timestamp_stripped.decode('utf-8'), "%B %d %Y"))
            else:
                timestamp.append(datetime.today())
        article_link_children = article_tags.find_all('a')
        article_link_tmp = article_link_children[0]
        article_link.append(
            article_link_tmp['href'].encode('utf-8', errors='ignore'))

    # NEXT PART: Figure out which dates are within a window
    # Which articles were posted within N days?
    is_recent = [
        datetime.today() - timedelta(days=days_ago) < x for x in timestamp
    ]
    link_indices = [i for i, x in enumerate(is_recent) if x]

    for i in range(0, len(link_indices)):
        page_result_link = article_link[link_indices[i]]
        page_result = requests.get(page_result_link)
        res_soup = BeautifulSoup(page_result.content, 'html.parser')
        story_tag = res_soup.find_all(class_="article-body__inner")
        if story_tag:  # Gracefully handle in case nothing comes up
            story_chunks = story_tag[0].find_all('p')
            story = [pt.get_text() for pt in story_chunks]
            story = ''.join(story)
            fetched_stories.append(story)

            title_tag = res_soup.find_all(class_="article-header__title")
            title_tag = title_tag[0].get_text()
            fetched_headlines.append(title_tag)

            all_text.append(title_tag)
            all_text.append(story)

    return all_text


################## Celebuzz scraper ############################################
def CelebuzzScraper(search_term, days_ago):

    from bs4 import BeautifulSoup
    import requests
    import string
    from datetime import datetime, timedelta
    import time
    from dateutil import parser
    import os

    # Take out any punctuation marks from name and convert to lowercase
    search_term = search_term.translate(
        str.maketrans('', '', string.punctuation))
    search_term = search_term.lower()

    # Format search term for the URL formula
    search_term_formatted = search_term.replace(" ", "+")
    page_link = "http://www.celebuzz.com/?s=" + search_term_formatted
    page = requests.get(page_link)
    soup = BeautifulSoup(page.content, 'html.parser')

    timestamp = []
    article_link_list = []
    headlines = []
    fetched_stories = []
    fetched_headlines = []
    all_text = []

    articles = soup.find_all(class_="post")

    # OK magazine doesn't give dates- it just lists in chronological order a lot of results.
    # So, grab maybe 4, and we'll check if each one is within the date range.
    for i in range(0, len(articles)):
        this_article = articles[i]

        result_tag = this_article.find_all('a')
        if result_tag:
            # Update headline list
            headline = result_tag[0].get_text()
            headlines.append(headline.strip())
            # Get the link
            link = result_tag[0]['href']
            link = link.encode('utf-8')
            article_link_list.append(link)
            # Get the date stamp in the correct format
            date_str = link[24:34]
            timestamp.append(parser.parse(date_str))

    # Which articles were posted within N days?
    is_recent = [
        datetime.today() - timedelta(days=days_ago) < x for x in timestamp
    ]
    link_indices = [i for i, x in enumerate(is_recent) if x]

    # Loop over the recent results
    for i in range(0, len(link_indices)):
        page_result_link = article_link_list[link_indices[i]]
        page_result = requests.get(page_result_link)
        res_soup = BeautifulSoup(page_result.content, 'html.parser')
        story_tag = res_soup.find_all(class_="article-content clearfix")
        story = story_tag[0].get_text()

        # append to lists!
        fetched_stories.append(story)
        fetched_headlines.append(headlines[link_indices[i]])

        all_text.append(headlines[link_indices[i]])
        all_text.append(story)

    return (all_text)


################# Nat'l Enquirer ##############################################
def NatlEnquirerScraper(search_term, days_ago):
    from bs4 import BeautifulSoup
    import requests
    import string
    from datetime import datetime, timedelta
    import re
    import time
    import os

    # Take out any punctuation marks from name and convert to lowercase
    search_term = search_term.translate(
        str.maketrans('', '', string.punctuation))
    search_term = search_term.lower()  #
    # Format search term for the URL formula
    search_term_formatted = search_term.replace(" ", "+")

    page_link = "http://www.nationalenquirer.com/search/?search=" + search_term_formatted
    page = requests.get(page_link)
    soup = BeautifulSoup(page.content, 'html.parser')

    articles = soup.find_all(class_="post-detail")
    timestamp = []
    article_link = []
    fetched_stories = []
    fetched_headlines = []
    fetched_subheads = []
    all_text = []

    # For every article on the page, get the link and the time it was posted at.
    for i in range(0, len(articles)):
        article_tags = articles[i]

        time_children = article_tags.find_all(class_="posted-date")
        if not time_children:
            timestamp.append(datetime.strptime('January 1 1900', "%B %d %Y"))
        else:
            timestamp_tmp = time_children[0].get_text()
            timestamp_stripped = re.findall('Posted (.*?) @', timestamp_tmp)
            timestamp_stripped = timestamp_stripped[0]

            timestamp_stripped = timestamp_stripped.encode(
                'utf-8', errors='ignore')
            timestamp_stripped = timestamp_stripped.translate(
                None, string.punctuation.encode('utf-8'))
            timestamp.append(
                datetime.strptime(
                    timestamp_stripped.decode('utf-8'), "%b %d %Y"))

        article_link_children = article_tags.find_all('a')
        article_link_tmp = article_link_children[0]
        article_link.append(
            article_link_tmp['href'].encode('utf-8', errors='ignore'))

    # Which results are recent?
    is_recent = [
        datetime.today() - timedelta(days=days_ago) < x for x in timestamp
    ]
    link_indices = [i for i, x in enumerate(is_recent) if x]

    # Loop over the recent results- DUMB. The national enquirer actually only has
    # headlines, no articles. All the articles are in the form of galleries. Sigh.
    for i in range(0, len(link_indices)):
        page_result_link = article_link[i]
        page_result = requests.get(page_result_link)
        res_soup = BeautifulSoup(page_result.content, 'html.parser')
        story_tag = res_soup.find_all(type="application/ld+json")
        if len(story_tag) > 1:
            story_tmp = story_tag[1].get_text()
            story = re.findall('caption":"(.*?)","url"', story_tmp)
            story = ' '.join(story)
            fetched_stories.append(story)
            title_tag = res_soup.find_all("title")
            title = title_tag[0].get_text()
            subtitle_tag = res_soup.find_all(class_="entry-subtitle")
            subtitle = subtitle_tag[0].get_text()
            fetched_headlines.append(title)
            fetched_subheads.append(subtitle)

            all_text.append(title)
            all_text.append(subtitle)
            all_text.append(story)

    return (all_text)


############# TMZ #############################################################
def TMZScraper(search_term, days_ago):
    from bs4 import BeautifulSoup
    import requests
    import string
    import re
    from selenium import webdriver
    from dateutil import parser
    from datetime import datetime, timedelta
    import time
    from html.parser import HTMLParser
    import os
    from sys import platform

    h = HTMLParser()

    # Take out any punctuation marks from name and convert to lowercase
    search_term = search_term.translate(
        str.maketrans('', '', string.punctuation))
    search_term = search_term.lower()

    # Format search term for the URL formula
    search_term_formatted = search_term.replace(" ", "+")

    page_link = "http://tmz.com/search/news/" + search_term_formatted + "?adid=TMZ_Web_Nav_Search"
    domain = "http://www.tmz.com"

    # if platform == "linux" or platform == "linux2":
    #     cwd = os.getcwd()
    #     browser = webdriver.Chrome(cwd + '/chromedriver')
    # elif platform == "win32" or platform == "win64":
    #     browser = webdriver.Chrome()
    # else:
    #     cwd = os.getcwd()
    #     browser = webdriver.Chrome(cwd + '/chromedriver')
    browser = webdriver.PhantomJS()

    browser.get(page_link)
    html = browser.page_source
    browser.close()
    browser.quit()

    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all(class_="title")  # This will get some junk, too.

    #### Initialize the vectors for storing results
    timestamp = []
    article_link_list = []
    fetched_stories = []
    fetched_headlines = []
    all_text = []

    for i in range(1, len(articles)):
        child = articles[i].find_all(class_="has-adid")

        # If it really is a search result- as in, child isn't empty-
        if child:
            headline = child[0].get_text()
            link = child[0]['href']
            article_link_list.append(link.encode('utf-8', errors='ignore'))
            date = link[1:12].encode(
                'utf-8', errors='ignore'
            )  # TMZ encodes date strings in first 12 char of URL
            timestamp.append(parser.parse(date))

    ##### Of the results we got, how many are recent enough?
    is_recent = [
        datetime.today() - timedelta(days=days_ago) < x for x in timestamp
    ]
    link_indices = [i for i, x in enumerate(is_recent) if x]

    # Loop over the recent results
    for i in range(0, len(link_indices)):

        page_result_link = domain + article_link_list[link_indices[i]].decode(
            'utf-8')
        page_result = requests.get(page_result_link)
        res_soup = BeautifulSoup(page_result.content, 'html.parser')
        story_tag = res_soup.find_all(type="application/ld+json")
        story_tmp = story_tag[0].get_text()
        story = re.findall('articleBody": "(.*?)"\n}', story_tmp)

        # Clean up the text- TMZ litters with HTML string
        story = story[0].replace('\\n', ' ')
        story = h.unescape(story)
        story = story.replace('\\', ' ')

        headline = re.findall('headline": "(.*?)",', story_tmp)
        headline = h.unescape(headline[0])

        fetched_stories.append(story)
        fetched_headlines.append(headline)
        all_text.append(headline)
        all_text.append(story)

    return all_text


######################## OK Magazine ##########################################
def OKScraper(search_term, days_ago):
    from bs4 import BeautifulSoup
    import requests
    import string
    from datetime import datetime, timedelta
    import time
    from dateutil import parser
    import os
    import re

    # Take out any punctuation marks from name and convert to lowercase
    search_term = search_term.translate(
        str.maketrans('', '', string.punctuation))
    search_term = search_term.lower()

    # Format search term for the URL formula
    search_term_formatted = search_term.replace(" ", "+")

    page_link = "http://okmagazine.com/search/?search=" + search_term_formatted
    page = requests.get(page_link)
    soup = BeautifulSoup(page.content, 'html.parser')

    timestamp = []
    article_link_list = []
    headlines = []
    fetched_stories = []
    fetched_headlines = []
    final_fetched_stories = []
    final_fetched_headlines = []
    all_text = []

    articles = soup.find_all("article")

    # OK magazine doesn't give dates- it just lists in chronological order a lot of results.
    # So, grab maybe 4, and we'll check if each one is within the date range.
    for i in range(0, min(len(articles), 4)):
        this_article = articles[i]

        headline_tag = this_article.find_all(class_="promo-title")
        link_tag = this_article.find_all("a")

        # Update headline list
        headline = headline_tag[0].get_text()
        headlines.append(headline)

        # Get the link
        link = link_tag[0]['href']
        article_link_list.append(link.encode('utf-8'))

    # NEXT PART: Figure out which dates are within a window
    for i in range(0, len(headlines)):
        page_result_link = article_link_list[i]
        page_result = requests.get(page_result_link)
        res_soup = BeautifulSoup(page_result.content, 'html.parser')
        story_tag = res_soup.find_all(class_="gallery-item-caption")
        story = ""
        for j in range(0, len(story_tag)):
            story_tmp = story_tag[j].get_text()
            story_tmp = story_tmp
            story += story_tmp

        # Also get the date it occurred on
        date_tag = res_soup.find_all(class_="posted-date")
        date_str = date_tag[0].get_text()
        date_str = date_str.encode('utf-8').strip()
        date_str = date_str.decode('utf-8')
        datestripped = datetime.strptime(date_str, '%B %d, %Y %H:%M%p')
        #date = re.findall('.* [0-9]{2}, [0-9]{4}', date_str.decode('utf-8'))

        # Append to master lists
        fetched_stories.append(story)
        fetched_headlines.append(headlines[i])
        timestamp.append(datestripped)

    # Which articles were posted within N days?
    is_recent = [
        datetime.today() - timedelta(days=days_ago) < x for x in timestamp
    ]
    link_indices = [i for i, x in enumerate(is_recent) if x]

    # Write results to a CSV.
    #results_loc = os.getcwd() + "/Results/"
    #file_base = results_loc + "/OKMagazine_" + search_term.lower().replace(" ", "_") + "_" + time.strftime("%d_%m_%y")
    for item in range(0, len(link_indices)):
        # Find out what our file number should be
        file_num = item
        '''
        f = open(file_base + '_headline_' + str(file_num) + ".txt","w")
        f.write("%s/n" % fetched_headlines[link_indices[item]])
        f.close()
        '''
        final_fetched_headlines.append(fetched_headlines[link_indices[item]])
        all_text.append(fetched_headlines[link_indices[item]])

    for item in range(0, len(link_indices)):
        # Find out what our file number should be
        file_num = item
        '''
        f = open(file_base + '_article_' + str(file_num) + ".txt","w")
        f.write("%s/n" % fetched_stories[link_indices[item]])
        f.close()
        '''
        final_fetched_stories.append(fetched_stories[link_indices[item]])
        all_text.append(fetched_stories[link_indices[item]])
    return all_text


def tabloid_search(search_term_string, num_days_ago):
    num_days_ago = int(num_days_ago)
    print("STARTING SEARCH WITH: %s, %d" % (search_term_string, num_days_ago))
    all_text = []
    yield '.'
    all_text += EScraper(search_term_string, num_days_ago)
    yield '.'
    all_text += RadarScraper(search_term_string, num_days_ago)
    yield '.'
    all_text += PerezScraper(search_term_string, num_days_ago)
    yield '.'
    all_text += PeopleScraper(search_term_string, num_days_ago)
    yield '.'
    all_text += CelebuzzScraper(search_term_string, num_days_ago)
    yield '.'
    all_text += NatlEnquirerScraper(search_term_string, num_days_ago)
    yield '.'
    all_text += TMZScraper(search_term_string, num_days_ago)
    yield '.'
    all_text += OKScraper(search_term_string, num_days_ago)
    yield ''.join(all_text)


def command_line_write():
    search_term_string = get_search_term_from_user()
    num_days_ago = int(get_days_ago_from_user())
    destination = get_destination_from_user()
    EScraped_text = EScraper(search_term_string, num_days_ago)
    write_results_to_file(EScraped_text, destination)
    RadarScraped_text = RadarScraper(search_term_string, num_days_ago)
    write_results_to_file(RadarScraped_text, destination)
    PerezScraped_text = PerezScraper(search_term_string, num_days_ago)
    write_results_to_file(PerezScraped_text, destination)
    PeopleScraped_text = PeopleScraper(search_term_string, num_days_ago)
    write_results_to_file(PeopleScraped_text, destination)
    CelebuzzScraped_text = CelebuzzScraper(search_term_string, num_days_ago)
    write_results_to_file(CelebuzzScraped_text, destination)
    NatlEnquirerScraped_text = NatlEnquirerScraper(search_term_string,
                                                   num_days_ago)
    write_results_to_file(NatlEnquirerScraped_text, destination)
    TMZScraped_text = TMZScraper(search_term_string, num_days_ago)
    write_results_to_file(TMZScraped_text, destination)
    OKScraped_text = OKScraper(search_term_string, num_days_ago)
    write_results_to_file(OKScraped_text, destination)


if __name__ == "__main__":
    command_line_write()
