from django.shortcuts import render

def home(request, context=''):
    if context == '':
        context={'name':'Pierrick Pagaud',
                'about':'''Beyond the Indian hamlet, upon a forlorn strand, I happened on a trail
                of recent footprints. Through rotting kelp, sea cocoa-nuts & bamboo, the
                tracks led me to their maker, a White man, his trowzers & Pea-jacket
                rolled up, sporting a kempt beard & an outsized Beaver, shoveling &
                sifting the cindery sand with a teaspoon so intently that he noticed me
                only after I had hailed him from ten yards away. Thus it was, I made the
                acquaintance of Dr. Henry Goose, surgeon to the London nobility. His
                nationality was no surprise. If there be any eyrie so desolate, or isle so
                remote, that one may there resort unchallenged by an Englishman, ’tis
                not down on any map I ever saw.'''}
    return render(request, 'home.html', context)