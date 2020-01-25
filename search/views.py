import requests
from django.shortcuts import render
from django.conf import settings
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from isodate import parse_duration


def max_retry():
    """ To manage MUltiple request"""
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def index(request):
    videos = []
    if request.method == "POST":
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        video_url = 'https://www.googleapis.com/youtube/v3/videos'

        search_params = {
            'part': 'snippet',
            'q': request.POST['search'],
            'key': settings.YOUTUBE_DATA_API_KEY,
            'maxResults': 6,
            'type': 'video'
        }
        video_ids = []
        req = max_retry()
        r = req.get(search_url, params=search_params)
        print("value of r is", r.text)
        results = r.json()['items']
        for result in results:
            video_ids.append(result['id']['videoId'])

        video_params = {
            'part': 'snippet, contentDetails',
            'key': settings.YOUTUBE_DATA_API_KEY,
            'id': ','.join(video_ids),
            'maxResults': 6,
        }    
        req = max_retry()
        r = req.get(video_url, params=video_params)
        results = r.json()['items']
        for result in results:
            try:
                tags = result['snippet']['tags']
            except KeyError:
                continue
            video_data = {
                'title': result['snippet']['title'],
                'id': result['id'],
                'url': f'https://www.youtube.com/watch?v={ result["id"] }',
                'tags': tags,
                'duration': int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
                'thumbnail': result['snippet']['thumbnails']['high']['url']
            }
            videos.append(video_data)
    context = {
        'videos': videos
    }
    return render(request, 'search/index.html', context)
