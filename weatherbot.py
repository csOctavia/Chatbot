#!../env/bin/python
import sys

from city import City
from query import Query
import intent_functions

if __name__ == "__main__":
    training_mode = '-t' in sys.argv

    question = ''
    City.read()
    print('Hello I am Weatherbot. I know about the weather in most cities around the world :) Go ahead and ask.')

    while True:
        question = input('? ').lower()
        query = Query(question, filtered=False)
        matched_query = query.get_match()
        if query.filtered_text!=matched_query.filtered_text and training_mode:
        # TRAINING
            while True:
                print(f'<{matched_query.tag}> {matched_query.filtered_text}')
                correct = input('Is this correct (y/n)? ').lower()
                if correct == 'n':
                    # ask the user which one is the correct intent tag
                    all_tags = [tag for tag in Query.all_tags() if tag is not None] + [None]
                    for cnt, tag in enumerate(all_tags):
                        print(f'{cnt}. {tag}')
                    while True:
                        try:
                            tag_no = int(input('> '))
                        except ValueError:
                            continue
                        if tag_no in range(len(all_tags)):
                            query.tag = all_tags[tag_no]
                            break
                    break
                elif correct == 'y':
                    query.tag = matched_query.tag
                    break
        # END TRAINING
        else:
            query.tag = matched_query.tag

        if query.tag == 'hi':
            print('Hi there. Ask me about the weather.')
        elif query.tag == 'bye':
            print('Later, gator!')
            break
        elif query.tag == 'chatter':
            print('My social skills are underdeveloped. Ask me about the weather.')
        elif query.tag == 'debug':
            if training_mode:
                import pdb; pdb.set_trace()
            else:
                continue
        else:
            try:
                # call the intent function by introspection
                getattr(intent_functions, query.tag)(query)
            except AttributeError:
                print(f'>> Can\'t handle this tag! ({query.tag}) <<')

    if training_mode:
        Query.write() # output updated intents.json
