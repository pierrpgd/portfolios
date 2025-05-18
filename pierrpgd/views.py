from django.shortcuts import render
from .models import Profile, About, Experience, Project

def home(request, context=''):
    if context == '':
        # Créer ou récupérer le profil
        profile, created = Profile.objects.get_or_create(name='Pierrick Pagaud')

        about = [
                '''Beyond the Indian hamlet, upon a forlorn strand, I happened on a trail
                of recent footprints. Through rotting kelp, sea cocoa-nuts & bamboo, the
                tracks led me to their maker, a White man, his trowzers & Pea-jacket
                rolled up, sporting a kempt beard & an outsized Beaver, shoveling &
                sifting the cindery sand with a teaspoon so intently that he noticed me
                only after I had hailed him from ten yards away. Thus it was, I made the
                acquaintance of Dr. Henry Goose, surgeon to the London nobility. His
                nationality was no surprise. If there be any eyrie so desolate, or isle so
                remote, that one may there resort unchallenged by an Englishman, ’tis
                not down on any map I ever saw.''',
                '''Had the doctor misplaced anything on that dismal shore? Could I
                render assistance? Dr. Goose shook his head, knotted loose his ‘kerchief
                & displayed its contents with clear pride. “Teeth, sir, are the enameled
                grails of the quest in hand. In days gone by this Arcadian strand was a
                cannibals’ banqueting hall, yes, where the strong engorged themselves
                on the weak. The teeth, they spat out, as you or I would expel cherry
                stones. But these base molars, sir, shall be transmuted to gold & how? An
                artisan of Piccadilly who fashions denture sets for the nobility pays
                handsomely for human gnashers. Do you know the price a quarter pound
                will earn, sir?”''',
                '''I confessed I did not.'''
        ]
        
        # Créer les paragraphes About
        for i, content in enumerate(about):
            About.objects.update_or_create(
                profile=profile,
                order=i,
                defaults={'content': content}
            )
        
        experience = [
            {
                'dates':'MAR. 2023 - MAR. 2025',
                'company':'Alpha 3i',
                'location':'Jacksonville FL, USA',
                'position':'Ingénieur logiciel MES',
                'description':'''Conception, développement et intégration de modules MES au sein de systèmes
                ERP pour des acteurs industriels de secteurs variés (aéronautique, santé, automobile).'''
            },
            {
                'dates':'SEP. 2019 - FEB. 2023',
                'company':'PAPREC France',
                'location':'Lyon, FRA',
                'position':'Chef de projet informatique junior',
                'description':'''Déploiement d'une plateforme IoT pour l'activité Collecte et Transports de déchets.'''
            },
            {
                'dates':'SEP. 2018 - SEP. 2019',
                'company':'PAPREC France',
                'location':'Lyon, FRA',
                'position':'Assistant chef de projet informatique (alternance)',
                'description':'''Déploiement d’une application web d’optimisation de circuit pour l’activité
                Collecte et Transports de déchets.'''
            }
        ]
        
        # Créer les expériences
        for i, exp in enumerate(experience):
            Experience.objects.update_or_create(
                profile=profile,
                order=i,
                defaults={
                    'dates': exp['dates'],
                    'company': exp['company'],
                    'location': exp['location'],
                    'position': exp['position'],
                    'description': exp['description']
                }
            )
        
        # Créer le projet
        Project.objects.update_or_create(
            profile=profile,
            defaults={
                'title': 'This website',
                'description': 'Description du projet'
            }
        )

        context = {
            'profile': profile,
            'about': profile.about.all(),
            'experience': profile.experience.all(),
            'projects': profile.projects.all()
        }
    return render(request, 'home.html', context)