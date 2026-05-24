import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render
from .models import Score
from .models import Player

# Create your views here.
def leaderboard(request):
    scores = Score.objects.select_related("player")[:10]
    return render(request,"game/leaderboard.html",{"scores" : scores})

def play(request):
    return render(request,"game/play.html")

@require_POST
def submit_score(request):

    data = json.loads(request.body)

    player_name = data.get("name")
    points = data.get("points")

    if not player_name or points is None:
        return JsonResponse(
            {"error": "name and points are required"},
            status=400,
        )

    player, created = Player.objects.get_or_create(
        name=player_name
    )

    Score.objects.create(
        player=player,
        points=points,
    )

    return JsonResponse({
        "status": "ok"
    })
