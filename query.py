import json
import requests
import string
import datetime
from math import log10

import numpy
from scipy import spatial
from nltk import pos_tag
from nltk.tokenize import word_tokenize

from city import City

# NLP utility functions
def bag_of_words(tokens, vocabulary):
    bow = numpy.zeros(len(vocabulary))
    for word in tokens:
        try:
            index = vocabulary.index(word)
        except ValueError:
            continue
        bow[index] += 1
    return bow

def sim_cosine(vector_1, vector_2):
    similarity = 1 - spatial.distance.cosine(vector_1, vector_2)
    return similarity

def tfidf(*vectors):
    N = len(vectors)
    tfidf_vectors = [numpy.zeros(len(vectors[0])) for vector in vectors]
    for i in range(len(vectors[0])):
        term_booleans = []
        for j in range(len(vectors)):
            term_booleans.append(vectors[j][i] != 0)
        n =sum(term_booleans)
        for j in range(len(vectors)):
            frequency = vectors[j][i]
            tfidf = log10(1+frequency) * log10(N/n)
            tfidf_vectors[j][i] = tfidf
    return tfidf_vectors

# date parsing functions
day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

def get_next_date_by_day_name(day_name):
    today = datetime.date.today()
    try:
        day_index = day_names.index(day_name) % 7
    except ValueError:
        return None
    return today + datetime.timedelta( (day_index-today.weekday()) % 7 )

def try_to_parse_date(token):
    ... # to be implemented
    return None


class Query():
    # class variables, these are not to be accessed directly
    __all = None # all Query instances, access with Query.all()
    __vocab = [] # the vocabulary of all Query instances, access with Query.vocab()
    prev_cities = [] # "where" context
    prev_dates = [] # "when" context

    def __init__(self, text, tag=None, filtered=True):
        self.text = text
        self.tag = tag
        self.tokens = [word for word in word_tokenize(text.lower()) if word not in string.punctuation]
        if filtered:
            self.filtered_tokens = self.tokens
            self.filtered_text = ' '.join(self.filtered_tokens)
        else:
            self.filter_cities_and_dates()
        Query.__vocab = list(set(Query.__vocab + self.filtered_tokens))
        self.all().append(self)
    def __str__(self):
        return f'<{self.tag}> {self.text}'
    def __repr__(self):
        if self.tag is None:
            return f"Query('{self.text}')"
        return f"Query('{self.text}', '{self.tag}')"

    def update_prev(self):
        """ update where and when context """
        Query.prev_cities = list(reversed(self.cities))
        Query.prev_dates = list(reversed(self.dates))

    def get_match(self):
        """ return the closest query in the intents database """
        vectors = []
        all_tagged = [q for q in Query.all() if q.tag is not None]
        for query in all_tagged:
            vectors.append(bag_of_words(query.filtered_tokens, Query.__vocab))
        vectors.append(bag_of_words(self.filtered_tokens, Query.__vocab))
        vectors_tfidf = tfidf(*vectors)
        sims = []
        for vector_tfidf in vectors_tfidf[:-1]:
            sims.append(sim_cosine(vectors_tfidf[-1], vector_tfidf))
        ms = max(sims)

        return all_tagged[sims.index(ms)]

    def filter_cities_and_dates(self):
        """ separate space and time related tokens from regular words """
        self.cities = []
        self.dates = []
        self.filtered_tokens = []

        text = ' ' + ' '.join(self.tokens) + ' '

        # extract cities
        vocab = Query.vocab()
        names = set()
        for city in City.all():
            if city.name not in vocab and f' {city.name} ' in text:
                names.add(city.name)
        # ugly hack to not treat i.e. new york as york + new york
        to_remove = set()
        for name in names:
            for name1 in names:
                if name1!=name and name1 in name:
                    to_remove.add(name1)
        names = names - to_remove
        # end ugly hack
        for name in names:
            self.cities.append(City.get(name))
            text = text.replace(name, '').replace('  ', ' ')

        # extract dates
        for token in word_tokenize(text):
            if not token in vocab:
                maybe_date = try_to_parse_date(token)
                if maybe_date:
                    self.dates.append(maybe_date)
                elif token=='today':
                    self.dates.append(datetime.date.today())
                elif token=='tomorrow':
                    self.dates.append(datetime.date.today() + datetime.timedelta(days=1))
                elif token in day_names:
                    self.dates.append(get_next_date_by_day_name(token))
                else:
                    self.filtered_tokens.append(token)
            else:
                self.filtered_tokens.append(token)

        self.filtered_text = ' '.join(self.filtered_tokens)

    def require_cities(self, city_count):
        """ update self.cities to at least a count of city_count cities, either from the current query if specified expclitily, or from the context """
        if len(self.cities) >= city_count: return
        prev_cities_gen = (city for city in Query.prev_cities)
        for _ in range(city_count-len(self.cities)):
            city = next(prev_cities_gen, None)
            if city is None:
                self.ask_for_city()
            else:
                self.cities.append(city)
    def require_dates(self):
        """ update self.dates from context if not available expclitily """
        if not self.dates:
            self.dates = Query.prev_dates
    def require(self, city_count):
        """ require_cities and require_dates """
        self.require_cities(city_count)
        self.require_dates()

    def ask_for_city(self):
        """ explicitly ask for a city (used when none is available in the context) """
        city_name = input('What city, please? ').lower()
        city = City.get(city_name)
        if city is not None:
            self.cities.append(city)
        else:
            print('Sorry I don\'t know that city. Please ask me something else.')

    @classmethod
    def all(cls):
        """ return all Query instances """
        if cls.__all is None:
            cls.read()
        return cls.__all

    @classmethod
    def vocab(cls):
        """ return the vocabulary of all Query instances """
        if cls.__all is None:
            cls.read()
        return cls.__vocab

    @classmethod
    def read(cls, file_name='intents.json'):
        """ read the training data """
        ... # check file exists
        with open(file_name) as f:
            intents_json = json.load(f)
        # {'tag': 'query_temperature', 'patterns': []}
        cls.__all = []
        for intent in intents_json:
            for text in intent['patterns']:
                Query(text, intent['tag'])
    @classmethod
    def write(cls, file_name='intents.json'):
        """ write the training data """
        data = []
        for tag in cls.all_tags():
            data.append(
                {
                    'tag': tag,
                    # 'patterns': cls.get_texts_by_tag(tag),
                    'patterns': list(set([q.filtered_text for q in cls.all() if q.tag==tag])),
                }
            )
        with open(file_name, 'w') as f:
            json.dump(data, f)

    @classmethod
    def all_tags(cls):
        """ return a list of all intent tags """
        tags = []
        for q in cls.all():
            tags.append(q.tag)
        return list(set(tags))
