# import
import tmdbsimple as tmdb
import requests
import json
from datetime import date
import os.path
API_KEY = '1af5a2f9d3820fa8f1c3de90181a7129'
tmdb.API_KEY = '1af5a2f9d3820fa8f1c3de90181a7129'

# Original search for TMDB ID
search = tmdb.Search()
response = search.movie(query=input('Movie Title: '))
response_results = response['results']
response_0 = response_results[0]
tmdb_id = response_0['id']
print("The movie ID is: " + str(tmdb_id))

# TMDB API Requests
URL = 'https://api.themoviedb.org/3/movie/' + str(tmdb_id) + '?api_key=' + API_KEY
print("The movie URL is: " + str(URL))
Basic_URL = requests.get(URL)
Basic_text = Basic_URL.content
Basic_data = json.loads(Basic_text.decode('utf-8'))
URL = 'https://api.themoviedb.org/3/movie/' + str(tmdb_id) + '/credits?api_key=' + API_KEY
print("The credits URL is: " + str(URL))
Credits_URL = requests.get(URL)
Credits_text = Credits_URL.content
Credits_data = json.loads(Credits_text.decode('utf-8'))
URL = 'https://api.themoviedb.org/3/movie/' + str(tmdb_id) + '?api_key=' + API_KEY + '&language=en-US&append_to_response=release_dates'
print("The release dates URL is: " + str(URL))
MPAA_URL = requests.get(URL)
MPAA_text = MPAA_URL.content
MPAA_data = json.loads(MPAA_text.decode('utf-8'))

# Get MPAA rating
mpaa = ''
all_dates = (MPAA_data['release_dates']['results'])
for x in range(len(all_dates)):
    if (all_dates[x]["iso_3166_1"]) == "US":
        mpaa = ('Rated ' + all_dates[x]["release_dates"][0]['certification'])

# Pull cast members based on popularity rating, reduces output size
cast = Credits_data['cast']
cast_list = []
for x in range(len(cast)):
    if (cast[x]['popularity']) > 5:
        cast_member = {}
        y = cast[x]
        z = y['name']
        cast_member['name'] = z
        a = y['character']
        cast_member['character'] = a
        b = y['order']
        cast_member['order'] = b
        # c = y['popularity']
        # cast_member['popularity'] = c
        cast_list.append(cast_member)

# Pull important crew members
crew = Credits_data['crew']
Director = ''
Screenplay = ''
Producer = ''
for x in range(len(crew)):
    if (crew[x]['job']) == 'Director':
        Director = (crew[x]['name'])
    if (crew[x]['job']) == 'Screenplay':
        Screenplay = (crew[x]['name'])
    if (crew[x]['job']) == 'Producer':
        Producer = (crew[x]['name'])

# Generate Variables for HTML, in order of use in HTML
original_title = Basic_data['original_title']
vote_average = Basic_data['vote_average']
vote_count = Basic_data['vote_count']
outline = Basic_data['overview']
tagline = Basic_data['tagline']
runtime = Basic_data['runtime']
# MPAA
# tmdb ID
unique_id = Basic_data['imdb_id']
genres = Basic_data['genres']
genre_name = []
[genre_name.insert(0, genres[x]['name']) for x in range(len(genres))]  # and other genre info
country = (Basic_data['production_countries'][0]['name'])
set_name = input("Set Name (leave blank if single): ")
# See important people, credits section
premiered = Basic_data['release_date']
year = premiered[:4]
studio = (Basic_data['production_companies'][0]['name'])
# See actors section
date_added = date.today().strftime('%Y-%m-%d')

# HTML for .nfo output
NFO = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<movie>
    <title>{original_title}</title>
    <originaltitle>{original_title}</originaltitle>
    <ratings>
        <rating name="imdb" max="10" default="true">
            <value>{vote_average}</value>
            <votes>{vote_count}</votes>
        </rating>
    </ratings>
    <userrating></userrating>
    <outline>{outline}</outline>
    <plot>{outline}</plot>
    <tagline>{tagline}</tagline>
    <runtime>{runtime}</runtime>
    <fanart></fanart>
    <mpaa>{mpaa}</mpaa>
    <playcount></playcount>
    <lastplayed></lastplayed>
    <id>{tmdb_id}</id>
    <uniqueid type="imdb" default="true">{unique_id}</uniqueid>'''.format(**locals())
for x in range(len(genre_name)):
    NFO += f'''
    <genre>{genre_name[x]}</genre>'''.format(**locals())
NFO += f'''
    <country>{country}</country>
    <set>
        <name>{set_name}</name>
    </set>
    <credits>{Director}</credits>
    <credits>{Screenplay}</credits>
    <credits>{Producer}</credits>
    <director>{Director}</director>
    <premiered>{premiered}</premiered>
    <year>{year}</year>
    <studio>{studio}</studio>'''.format(**locals())
for x in range(len(cast_list)):
    NFO += f'''
    <actor>
        <name>{(cast_list[x]['name'])}</name>
        <role>{(cast_list[x]['character'])}</role>
        <order>{(cast_list[x]['order'])}</order>
        <thumb></thumb>
    </actor>'''.format(**locals())
NFO += f'''
    <resume>
        <position></position>
        <total></total>
    </resume>
    <dateadded>{date_added}</dateadded>
<movie>'''.format(**locals())
print(NFO)

# output
if input('Does this file look correct (True or False): ') == 'True':
    # save_path = 'C:/Users/mnsho/PycharmProjects/NFO Creator/NFO Files'
    save_path = input('Save Path (leave blank to save in folder): ')
    name_of_file = str(original_title + ' (' + year + ').nfo')
    completeName = os.path.join(save_path, name_of_file)
    _nfo = open(completeName, 'w')
    _nfo.write(NFO)
else:
    print('Mission Aborted')
