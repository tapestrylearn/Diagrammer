import requests
import json
import numpy as np

endpoint = 'https://language.googleapis.com/v1/documents:analyzeSentiment'
headers = {'Authorization': 'Bearer ya29.c.Ko8B3Ad3uCkxKXY7JjXsPng6O4dtbd0TF4SWgA7zEDbH55Qklr_zAFiQWfmK-o7koIiyF8bJvaU-JPA6cNYwR9bO2Cy_E5WFBC-0cddGXmUNPvpPE-amwA1sd9pEeQXIjkCW-NshfhK_1DQBfxc1--uwpghLmGOafK5shhlgvAbi-kFzxLrvGoBcWI3vGz2WoCU'}

insult = ['Wow, you are a prime example of dogshit journalism!', 'i feel like im the only one watching this dribble', 'Shut up monkey', 'this is some basic white girl stuff', 'Idk whats worse, no masks, her tone or those boots', 'Worst stream ever. Impossible to follow.', 'Shes kinda meh tbh', 'Damn, needs more masks', 'Dude sounds like the micro machines guy', 'She had a honkeytonk badonkadonk', 'probably about 16 protestors and 90 vloggers', "you're a dumbass", 'get out verified journalist scum', 'what a pretentious asshole']
off_topic = ['Any girls free for fun?', 'How do I get a girlfriend?', 'You need a huge monster size d!ck to got one or many girlfriend.', 'are you fortnite 2']
racist = ['I see white people', 'fuck black people', "it's the chinese again", 'get out of here mexicans']
insensitive = ['9/11 was the greatest day of my life', 'More dead this year than in Iraq', 'the day iran got a 2k killstreak', 'Hide and seek champion osama bin laden', 'We get to see people get shot?']
aggressive_questions = ['What’s the difference in the left stoking fears of earth burning?', '“We know”, that’s supposed to be evidence?', 'Rhode Island is your size example?', 'Kamala is doing a rally in nv this week. What’s your point?', 'What has Gov Newsom done to reduce undergrowth?', 'You ok with Portland Antifa?', 'so permits are not something people like so therefore dont apply? Is this the line of thinking?', 'you mean the system of law and order?']
criticism = ['Its liberal policies that have done this', 'permits only apply to conservative protests', 'all these democrat run cities are going to be running out of tax revenue soon', '“we keep us safe”, that’s why 1000s have died in Chicago from violence', 'These marches do nothing at all besides annoy people', 'Maybe if they annoy enough people and inconvenience enough people something will start to break free.', "permits are a thing like in DC where *everyone* wants to protest. it's like a reservation at a restaurant. :-)", 'You have the freedom to request a permit to protest an oppressive system. -signed oppressive system.', 'These marches have been going on for a few months now and nothing has really change', 'Before 2020, if people blocked the roads it would be ruled unlawful assembly if you did not have a permit', 'Trump could care a less about blm and biden just uses blm for votes', 'I doubt we see any difference in december regardless of who wins in november', 'How come u dont protest when a 5 year gets gunned down by gang cross fire', 'bruh these protests just piss off regular people trying to get home to their families. you want actualy change, take it to the system, not the people', 'just fighting for the agenda']
control = ['Yes!! Love to watch draw', 'Connection much better than recently', 'This is amazing to watch.', 'Just watched this video with Trump…stunning.', 'ooo trump', 'Spot on with this liza 👍☺️', '(Ann) as 🇨🇦, this is scary! It’s insane.', 'WE AGREE TRUMP WILL WIN RE-ELECTION VICTORY WITH 407 electoral college and 75 million popular votes', 'So fascinating watching your commentary through art. Thank you Liza!', 'Really cool liza']

array_names = ['criticism']
all_scores = {}

for array_name in array_names:
    all_scores[array_name] = []

    for text in eval(array_name):
        d = {
            'encodingType': 'UTF8',
            'document': {
                'type': 'PLAIN_TEXT',
                'content': text
            }
        }

        print(d, headers)

        result = requests.post(endpoint, json=d, headers=headers)
        print(result.json())
        score = result.json()['documentSentiment']['score']
        all_scores[array_name].append(score)
        print(text)
        print(score)
        print()

for array_name, scores in all_scores.items():
    print(array_name + ': ', end='')
    print(('%.3f' % (sum(scores) / len(scores))) + ' ', end = '')
    print('%.3f' % np.std(scores))
