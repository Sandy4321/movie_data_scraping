import urllib2
import re
import csv
from pprint import pprint

from bs4 import BeautifulSoup, SoupStrainer

base_url="http://www.boxofficemojo.com"
category_url="/movies/alphabetical.htm?letter="
starting_category="NUM"
categories="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
page_url="&page="
sub_pages=range(1, 16)

def link_data_saver(linkdict):
    with open("boxofficemojo_link_data.csv", "wb") as csv_file:
        writer = csv.writer(csv_file)
        for key, value in linkdict.items():
            writer.writerow([key, value])

def movie_data_saver(datadict):
    with open("boxofficemojo_movie_data.csv", "wb") as csv_file:
        headers = ["movie title", "domestic total gross", "release date", "runtime", "rating"]
        dict_writer = csv.DictWriter(csv_file, headers)
        dict_writer.writeheader()
        dict_writer.writerows(datadict)


def get_movie_value(soup, field_name):
    """
    takes a string attr of a movie on the page, and returns the string in the next sibling object (the value for that attribute)
    """
    obj = soup.find(text=re.compile(field_name))
    if not obj: return None
    next_sibling = obj.findNextSibling()
    if next_sibling:
        return next_sibling.text
    else: 
        return None

def page_parser(url="http://www.boxofficemojo.com/movies/?id=biglebowski.htm"):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    title_string = soup.find('title').text
    title_string.split("(")[0].strip()
    dtg = get_movie_value(soup, "Domestic Total")
    runtime = get_movie_value(soup, "Runtime")
    rating =  get_movie_value(soup, "MPAA Rating")
    release_date = get_movie_value(soup, "Release Date")
    return dict(zip(headers, [title_string, dtg, release_date, runtime, rating, url]))



def link_grabber(url):
    '''
    grabs all the movie links from a page and returns a dictionary of them along with additional info
    '''
    link_dict = {}
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    print "processing " + url

    for item in soup.find_all('a'):
        if item.has_attr('href'):
            if item['href'][:11] == "/movies/?id":
                full_row = [i.next_element for i in soup.find_all('a') if i['href'][:11] == "/movies/?id"]
                link = item['href']
                title = item.next_element.string
                studio = item.next_element.next_element.string
                total_gross = item.next_element.next_element.string
                total_theaters = item.next_element.next_element.next_element.string
                # opening_gross = 
                # opening_theaters = 
                # opening_date = 
                link_dict.update({base_url + link: {"title":title, "studio":studio, "total gross":total_gross, "total theaters":total_theaters,}})
    return link_dict


# list_of_titles = [i.string for i in soup.find_all('a') if i['href'][:11] == "/movies/?id"]
# list_of_links = [i['href'] for i in soup.find_all('a') if i['href'][:11] == "/movies/?id"]
# full_link = [i for i in soup.find_all('a') if i['href'][:11] == "/movies/?id"]
# alt_full_link = soup.select('a[href^=/movies/?id=]')
# full_rows = [i.parent.parent.parent for i in soup.find_all('a') if i['href'][:11] == "/movies/?id"]

pprint(link_grabber("http://www.boxofficemojo.com/movies/alphabetical.htm?letter=A&p=.htm"))

def movie_links():
    for page in [base_url + category_url + letter + page_url + str(number) for number in sub_pages for letter in categories]:
        link_grabber(page)

#makes a dictionary where each key is a url and each value is a bool indicating whether or not the page has been scraped for links

# master_dict = {base_url: False}
# for _ in range(3):
#     #go through all of the links grabbed and checks for ones that havent been scraped
#     unfinished_links = [link for link,record in master_dict.iteritems() if record == False]
#     for index, new_link in enumerate(unfinished_links):
#         #check whether dict item already exists, if it does then do nothing. if it does not then add with value False
#         for link in link_grabber(new_link):
#             full_link = base_url if link == base_url else base_url+link
#             if full_link not in master_dict: master_dict.update({full_link: False})
#         master_dict[new_link] = True

#link_data_saver(master_dict)

# master_dict.setdefault({base_url: False})

'''
begin at base url
scrape base url
add scraped base links to master_dict with link appended to base_url for complete path
mark base url as scraped (True)
go to any url in master_dict that is still False
scrape it and add links to master_dict and mark as True
end when no more links still False
'''





#movie_data = [page_parser(url) for url in url_list]
#check whether it is a legitimate movie page before calling page_parser by whether it begins with /movies
