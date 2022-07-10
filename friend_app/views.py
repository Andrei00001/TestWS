from django.shortcuts import render, reverse


def index(request):
    return render(request, 'index.html')


def login(request):
    return render(request, 'friend.html')


def room(request, room_name,token):
    return render(request, 'room.html', {
        'room_name': room_name,
        'token': token
    })
