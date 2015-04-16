import urllib2
import re
import json
from pprint import pprint
import time
from bs4 import BeautifulSoup, SoupStrainer
from brinery import *


def link_data_saver(linklist, filename="boxofficemojo_link_data.txt"):
    with open(filename, "wb") as txt_file:
        for item in linklist: 
            txt_file.write(item.encode("UTF-8"))
            txt_file.write("\n")

def movie_data_saver(datadict):
    with open("boxofficemojo_movie_data.json", "wb") as json_file:
        newData = json.dumps(datadict, sort_keys=True, indent=4) 
        json_file.write(newData) 

def read_main_dict():
    with open("boxofficemojo_movie_data.json", "rb") as json_file:
        return json.load(json_file)

def list_splitter(list, size=7):
    '''
    splits a list into separate lists of equal size
    '''
    return[ list[i:i+size] for i  in range(0, len(list), size) ]

def link_grabber(url, base_url="http://www.boxofficemojo.com"):
    '''
    grabs all the movie links from a page and returns a dictionary of them along with additional info
    '''
    link_dict = {}
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    header_row = soup.find(text=re.compile('Title')).parent.parent
    all_rows = soup.find(text=re.compile('Title')).parent.parent.find_all_next('td')
    row_font_values = [i.font for i in all_rows][4:-28]

    happy_list = list_splitter(row_font_values)
    for item in happy_list:
        link = unicode(item[0].find('a')['href'])
        title = unicode(item[0].string)
        studio = unicode(item[1].string)
        total_gross = unicode(item[2].string)
        total_theaters = unicode(item[3].string)
        opening_gross = unicode(item[4].string)
        opening_theaters = unicode(item[5].string)
        opening_date = unicode(item[6].string)
        link_dict.update({title: {"boxofficemojo url": base_url + link, "title":title, "studio":studio, "total gross":total_gross, "total theaters":total_theaters, "opening gross": opening_gross, "opening theaters":opening_theaters, "opening date":opening_date}})
    return link_dict

def movie_links(base_url="http://www.boxofficemojo.com"):
    category_url="/movies/alphabetical.htm?letter="
    categories= ["NUM"] + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    page_url="&page="
    sub_pages=range(1, 16)
    master_dict = {}
    link_list = []
    for page in [base_url + category_url + letter + page_url + str(number) for number in sub_pages for letter in categories]:
        link_list.append(page)
        print("processing " + page)
        master_dict.update(link_grabber(page))
    link_data_saver(link_list)
    return master_dict

def boxofficemojo_error_correction(main_dict=read_main_dict()):
    '''
    grab all the movies on site and their initial data plus links to their original pages and correct bad data
    '''
    temp_dict = main_dict
    temp_dict['Waiting for "Superman"'] = temp_dict.pop("None")
    temp_dict['Waiting for "Superman"']['title'] = 'Waiting for "Superman"'
    temp_dict['Offender']['studio'] = 'n/a'
    temp_dict['Toy Story 2 (3D)']['studio'] = 'BV'
    #below not working, whatev. edinting manually
    #getting Traceback (most recent call last):
        #   File "scrape.py", line 142, in <module>
        #     boxofficemojo_error_correction(movie_links())
        #   File "scrape.py", line 78, in boxofficemojo_error_correction
        #     temp_dict['Elizabeth'] = temp_dict.pop(unicode('Elizabeth\u00a0'))
        # KeyError: u'Elizabeth\\u00a0'
    # temp_dict['Elizabeth'] = temp_dict.pop('Elizabeth\u00a0')
    # temp_dict['Elizabeth']['title'] = 'Elizabeth'
    # temp_dict['Elizabeth']['boxofficemojo url'] = "http://www.boxofficemojo.com/movies/?id=elizabeth%A0.htm"
    # temp_dict['A Simple Plan'] = temp_dict.pop('A Simple Plan\u00a0')
    # temp_dict['A Simple Plan']['title'] = 'A Simple Plan'
    # temp_dict['A Simple Plan']['boxofficemojo url'] = "http://www.boxofficemojo.com/movies/?id=simpleplan%A0.htm"
    movie_data_saver(temp_dict)

def get_movie_value(soup, field_name):
    '''
    takes a string attr of a movie on the page, and returns the string in the next sibling object (the value for that attribute)
    '''
    obj = soup.find(text=re.compile(field_name))
    # if not obj: return None
    if not obj: raise Exception("cant find reference object")
    next_sibling = obj.findNextSibling()
    if next_sibling:
        return next_sibling.text
    else: 
        # return None
        raise Exception('cant find data for reference object')

def page_parser(url="http://www.boxofficemojo.com/movies/?id=biglebowski.htm", pickled=None):
    page = urllib2.urlopen(url) if pickled == None else pickled
    soup = BeautifulSoup(page)

    headers = ["url", "runtime", "rating", "genres", "actors"]
    # title_string = soup.find('title').text
    # title_string.split("(")[0].strip()
    try:
        #grab runtime
        runtime = unicode(get_movie_value(soup, "Runtime"))
    except:
        print("\n"+"*RUNTIME FAIL: "+url)
        runtime = "n/a"
    try:
        #grab rating
        rating =  unicode(get_movie_value(soup, "MPAA Rating"))
    except:
        print("\n"+"*RATING FAIL: "+url)
        rating = 'n/a'
    try:
        #grab genre
        temp = soup.find_all('a', href=re.compile("/genres/chart/"))
        genres = [i.string for i in temp]
        if unicode(get_movie_value(soup, 'Genre: ')) not in genres:
            genres.append(unicode(get_movie_value(soup, 'Genre: ')))
        # if not genres: raise Exception
    except:
        print("\n"+"*GENRE FAIL: "+url)
    try:
        #grab actors
        try:
            actors_block = soup.find(text=re.compile("Actors:")).next.next
        except:
            try:
                actors_block = soup.find(text=re.compile("Actor:")).next.next
            except:
                print("\n"+"*NO ACTORS FOUND: "+url)
        actors_string = actors_block.text
        messy_list = [a for a in re.split(r'([A-Z][a-z]*)', actors_string) if a]
        # [u'Jeff', u' ', u'Bridges', u'John', u' ', u'Goodman', u'Julianne', u' ', u'Moore', u'Steve', u' ', u'Buscemi', u'Philip', u' ', u'Seymour', u' ', u'Hoffman', u'Tara', u' ', u'Reid', u'Sam', u' ', u'Elliott', u'* (', u'Narrator', u')']
        name_list = []
        previous_name = None
        temp_name = ""
        messy_length = len(messy_list)
        #fix that mess
        error_list = [u' ', u"'", u'-', u'. ', u'Mc', u'Mac', u'De', u'Di', u'Da', u'Du', u' the ']
        for index, name in enumerate(messy_list):
            if name == "'" or name == '-':
                pass
            elif name not in error_list and previous_name not in error_list:
                name_list.append(temp_name)
                temp_name = ""
            elif index == messy_length-1:
                temp_name += name
                name_list.append(temp_name)
            temp_name += name
            previous_name = name
        name_list = filter(None, name_list)
        first_pass = name_list
        #remove any asterisks
        for index, item in enumerate(name_list):
            if item == u'* (':
                first_pass = name_list[:index]
                break
        second_pass = first_pass
        for index, item in enumerate(first_pass):
            if item == u'*':
                second_pass.pop(index)
            if item == u'.*':
                second_pass.pop(index)
                second_pass[index-1] += '.'
        third_pass = second_pass
        # open_paren_index = 0
        # dot_open_index = 0
        # close_paren_index = 0
        # for index, item in enumerate(third_pass):
        #     if item == '. (':

        actors = third_pass
    except:
        actors = []
    return dict(zip(headers, [url, runtime, rating, genres, actors]))

def refresh_masterdict():
    boxofficemojo_error_correction(movie_links())

def pickle_boxofficemojo_pages():
    list_of_links = [item['boxofficemojo url'] for item in read_main_dict().values()]
    link_data_saver(list_of_links, "boxofficemojo_movie_page_links.txt")
    print("\nSour pickle jar: "+str( brine_time(list_of_links, cap=10) ))

def the_big_merge():
    pass

# testing page parsing
url = "http://www.boxofficemojo.com/movies/?id=biglebowski.htm"
pickled = grab_pickle()
pprint(page_parser(url, pickled=pickled[url]))
# multple pages
start_time = time.time()
main_dict = read_main_dict()
for index, item in enumerate(main_dict.values()):
    if index == 100: break
    url = item['boxofficemojo url']
    records = page_parser(url, pickled=pickled[url])
    pprint(url)
    pprint(records['actors'])
pprint("Checked {0} links in {1} seconds.".format(index, time.time() - start_time))




# examples
# list_of_titles = [i.string for i in soup.find_all('a') if i['href'][:11] == "/movies/?id"]
# list_of_links = [i['href'] for i in soup.find_all('a') if i['href'][:11] == "/movies/?id"]
# full_link = [i for i in soup.find_all('a') if i['href'][:11] == "/movies/?id"]
# alt_full_link = soup.select('a[href^=/movies/?id=]')
# parent_cells = [i.parent.parent.next_sibling.next_sibling for i in soup.find_all('a') if i['href'][:11] == "/movies/?id"]
# siblign_cells = [i.find_next('td').contents for i in soup.find_all('a') if i['href'][:11] == "/movies/?id"]