import os
import re
import urllib
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm




def download_style(style, start=1):
    """downloads the image library of a given style (i.e. 'Impressionism', 
    'Expressionism', 'Cubism', etc.) and creates a csv file that includes all the info
    available from each artwork by scraping the list of artists that belong to the style first, 
    and then applying  download_artist for each of them.
    """
    url = f'https://www.wikiart.org/en/artists-by-art-movement/{style.lower()}/text-list'
    soup = BeautifulSoup(urllib.request.urlopen(url), "lxml")
    rows = soup.main.find_all('li')
    for i, row in enumerate(rows):
    #for i, row in enumerate(tqdm(rows)):
        if i < start-1: continue # to resume download in artwork #start
        artist = row.a.text
        #print(f'\n#{i+1}/{len(rows)}\t{artist}') # tqdm bars overlap with this
        tqdm.write(f'\n#{i+1}/{len(rows)}\t{artist}')
        download_artist(artist, start=1, print_info=False)




def download_artist(artist, start=1, print_info=False):
    """downloads the image library of a given artist and creates a csv file that includes all the info
    available from each artwork (date, style, genre, media, tag, location and dimensions).
    """    
    artworks = pd.read_csv('wikiart.csv', keep_default_na=False)
    url = f'https://www.wikiart.org/en/{"-".join(artist.lower().split())}/all-works/text-list'
    soup = BeautifulSoup(urllib.request.urlopen(url), "lxml")
    rows = soup.main.find_all('li')
    #for i, row in enumerate(rows):
    for i, row in enumerate(tqdm(rows)):    
        if i < start-1: continue # to resume download in artwork #start
        # link
        href = row.a.get('href')
        name_code = href.split('/')[-1]
        url = 'https://www.wikiart.org' + href
        soup = BeautifulSoup(urllib.request.urlopen(url), "lxml")
        # grabbing info
        title = soup.find('article').h3.text.strip()
        def extract_text(label, soup=soup):
            try:
                return ' '.join(soup.find(text=f'{label.title()}:').parent.parent.text.split(':')[1].strip().split('\n'))
            except:
                return 'N/A' # some are not always available
        date = extract_text('date') #
        style = extract_text('style')
        genre = extract_text('genre')
        media = extract_text('media') #
        tag = extract_text('tag') #
        location = extract_text('location') #
        dimensions = extract_text('dimensions') # 
        # downloading image     
        regex = r'https?://uploads[0-9]+[^/\s]+/\S+\.jpg'
        link_list = re.findall(regex, str(soup.html())) 
        try:
            download_link = [link for link in link_list if name_code in link and '!' not in link][0] 
            savepath = f'./{artist}/{name_code}.jpg'
            if not os.path.isdir(f'./{artist}'):
                os.mkdir(f'./{artist}')
            urllib.request.urlretrieve(download_link, savepath)  
        except IndexError:
            download_link = 'Not Found'
            if print_info:
                print(10*'\n'+ f'Error downloading #{i+1} "{title}" by {artist}: download link not found'+10*'\n') # name_code not in link
        # print check
        if print_info:
            print(f'\n#{i+1}/{len(rows)}')
            print(f'author:\t{artist}\ntitle:\t{title}\ndate:\t{date}\nstyle:\t{style}\ngenre:\t{genre}\nmedia:\t{media}\ndimns:\t{dimensions}\ntag:\t{tag}\nloc:\t{location}')
        # saving to csv
        info = {'author': artist, 'title': title, 'date': date, 'style': style, 'genre': genre, 'media': media, 'dimensions': dimensions, 'tag': tag, 'location': location, 'link': download_link, 'image': f'{name_code}.jpg'}   
        artworks = artworks.append(info, ignore_index=True)
        if i%50==0: artworks.to_csv('wikiart.csv', index=None) # saving periodically just in case
    artworks.to_csv('wikiart.csv', index=None)


  
  