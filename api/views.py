from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate,logout,login
from .serializers import AuthorSerializer
from base.models import Author, Category, Region, News
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import json
from datetime import datetime
from django.core.serializers import serialize

logger = logging.getLogger(__name__)

@csrf_exempt
def LoginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username is None or password is None:
            return HttpResponse('Missing username or password', status=400)
        try:
            currentAuthor = Author.objects.get(username=username)
        except Author.DoesNotExist:
            logger.warning('Failed login attempt for username: %s', username)
            return HttpResponse('Invalid Credentials', status=400)
        if currentAuthor.password == password:
            request.session['username'] = username
            return HttpResponse('Welcome, {}!'.format(currentAuthor.username), status=200)
        else:
            logger.warning('Failed login attempt for username: %s', username)
            return HttpResponse('Invalid Credentials', status=400)
    else:
        return HttpResponse('Invalid request', status=400)

@csrf_exempt
def LogoutView(request):
    if 'username' in request.session:
        request.session['username'] = None
    return HttpResponse('Goodbye!', status=200)

@csrf_exempt
def ManageStoriesView(request, key=None):
    if request.method == 'POST':
        return PostStoryView(request)
    elif request.method == 'GET':
        return GetStoryView(request)
    elif request.method == 'DELETE' and key is not None:
        return DeleteStoryView(request, key)
    else:
        return HttpResponse('Invalid request', status=400, content_type='text/plain')


@csrf_exempt
def PostStoryView(request):
    if request.method == 'POST':
        if request.session['username'] is None:
            return HttpResponse('Unauthenticated author', status=403)
        print(request.session['username'])
        currentAuthor = Author.objects.get(username=request.session.get('username'))
        data = json.loads(request.body)

        title = data.get('headline')
        if len(title) > 64:
            return HttpResponse('Error: Headline is too long. It should be up to 64 characters.', status=400, content_type='text/plain')
        category_short = data.get('category')
        if category_short not in ['pol', 'art', 'tech', 'trivia']:
            return HttpResponse("Error: Invalid category. It should be one of the following: 'pol', 'art', 'tech', 'trivia'.", status=400, content_type='text/plain')
        region_short = data.get('region')
        if region_short not in ['uk', 'eu', 'w']:
            return HttpResponse("Error: Invalid region. It should be one of the following: 'uk', 'eu', 'w'.", status=400, content_type='text/plain')
        details = data.get('details')
        if len(details) > 128:
            return HttpResponse('Error: Details are too long. They should be up to 128 characters.', status=400, content_type='text/plain')

        try:
            category = Category.objects.get(short=category_short)
            region = Region.objects.get(short=region_short)
        except ObjectDoesNotExist:
            return HttpResponse('Invalid category or region', status=503, content_type='text/plain')

        news = News.objects.create(
            title=title,
            category=category,
            region=region,
            author=currentAuthor,
            date=timezone.now().date(),
            details=details
        )

        return HttpResponse('Story posted successfully', status=201, content_type='text/plain')
    else:
        return HttpResponse('Invalid request', status=400, content_type='text/plain')

@csrf_exempt
def GetStoryView(request):
    if request.method == 'GET':
        cat = request.GET.get('story_cat', '*')
        reg = request.GET.get('story_region', '*')
        date = request.GET.get('story_date', '*')

        filters = {}
        if cat != '*':
            filters['category__name'] = cat
        if reg != '*':
            filters['region__name'] = reg
        if date != '*':
            try:
                date = datetime.strptime(date, '%d/%m/%Y').date()
                filters['date'] = date
            except ValueError:
                return HttpResponse('Invalid date format. Expected DD/MM/YYYY.', status=400)

        stories = News.objects.filter(**filters)
        serialized_filtered_stories = json.loads(serialize('json', stories))

        if not serialized_filtered_stories:
            return HttpResponse('No stories found', status=404)
        
        stories_list = []
        for story in serialized_filtered_stories:
            author = Author.objects.filter(pk=story["fields"]["author"])
            region = Region.objects.filter(pk=story["fields"]["region"])
            category = Category.objects.filter(pk=story["fields"]["category"])
            story_dict = {
                'key': story["pk"],
                'headline': story["fields"]["title"],
                'story_cat': category[0].name,
                'story_region': region[0].name,
                'author': author[0].firstName + ' ' + author[0].lastName,
                'story_date': story["fields"]["date"],
                'story_details': story["fields"]["details"],
            }
            stories_list.append(story_dict)

        return HttpResponse(json.dumps({'stories': stories_list}), content_type='application/json', status=200)
    else:
        return HttpResponse('Invalid request', status=400, content_type='text/plain')
    
@csrf_exempt
def DeleteStoryView(request, key):
    if request.method == 'DELETE':
        try:
            story = News.objects.get(pk=key)
            story.delete()
            return HttpResponse('Story deleted successfully', status=200, content_type='text/plain')
        except ObjectDoesNotExist:
            return HttpResponse('Story not found', status=503, content_type='text/plain')
    else:
        return HttpResponse('Invalid request', status=400, content_type='text/plain')

@csrf_exempt 
def getData(request):
    authors = Author.objects.all()
    serializer = AuthorSerializer(authors, many=True)
    return Response(serializer.data)