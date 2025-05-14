from django.shortcuts import render

def home(request, name="Pierrick Pagaud"):
    context={'name':name}
    return render(request, 'home.html', context)