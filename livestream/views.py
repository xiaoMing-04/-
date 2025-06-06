from django.shortcuts import render, redirect, get_object_or_404
from .models import Stream
from .services import create_livepeer_stream
import uuid
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def create_stream(request):
    if request.method == 'POST':
        stream_name = request.POST.get('stream_name', f"stream-{uuid.uuid4()}")
        stream_data = create_livepeer_stream(stream_name)
        try:
            stream = Stream.objects.create(
                name=stream_name,
                stream_id=stream_data['id'],
                rtmp_url="rtmp://rtmp.livepeer.com/live",
                stream_key=stream_data['streamKey'],
                playback_url=f"https://livepeercdn.com/hls/{stream_data['playbackId']}/index.m3u8"
            )
            return redirect('stream_detail', stream_id=stream.id)
        except Exception as e:
            return render(request, 'livestream/create_stream.html', {'error': str(e)})
    return render(request, 'livestream/create_stream.html')


def stream_detail(request, stream_id):
    stream = Stream.objects.get(id=stream_id)
    return render(request, 'livestream/stream_detail.html', {'stream': stream})


def stream_status(request, stream_id):
    stream = get_object_or_404(Stream, stream_id=stream_id)
    return JsonResponse({
        'is_live': True,
        'viewer_count': '123'
    })