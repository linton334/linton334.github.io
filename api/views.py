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
        category_short = data.get('category')
        region_short = data.get('region')
        details = data.get('details')

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
        service_id = request.GET.get('id', '*')
        cat = request.GET.get('cat', '*')
        reg = request.GET.get('reg', '*')
        date = request.GET.get('date', '*')

        filters = {}
        if service_id != '*':
            filters['service_id'] = service_id
        if cat != '*':
            filters['category__name'] = cat
        if reg != '*':
            filters['region__name'] = reg
        if date != '*':
            date = datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')
            filters['date__gte'] = date

        stories = News.objects.filter(**filters)

        if not stories:
            return HttpResponse('No stories found', status=404)

        stories_list = list(stories.values('key', 'headline', 'story_cat', 'story_region', 'author', 'story_date', 'story_details'))
        return JsonResponse({'stories': stories_list}, status=200)

    else:
        return HttpResponse('Invalid request', status=400)
    
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