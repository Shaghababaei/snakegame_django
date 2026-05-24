import json
from django.db.models import OuterRef, Subquery
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render
from .models import Score
from .models import Player

ALLOWED_PROFILE_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}
ALLOWED_PROFILE_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp",
}
MAX_PROFILE_IMAGE_SIZE = 10 * 1024 * 1024

# Create your views here.
def leaderboard(request):
    best_score_ids = Player.objects.annotate(
        best_score_id=Subquery(
            Score.objects.filter(player=OuterRef("pk"))
            .order_by("-points", "-created_at")
            .values("pk")[:1]
        )
    ).values("best_score_id")
    scores = (
        Score.objects.filter(pk__in=Subquery(best_score_ids))
        .select_related("player")
        .order_by("-points", "-created_at")[:10]
    )
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

    best_score = player.scores.order_by("-points", "-created_at").first()
    saved = False

    if best_score is None:
        Score.objects.create(
            player=player,
            points=points,
        )
        saved = True
    elif points > best_score.points:
        best_score.points = points
        best_score.save(update_fields=["points"])
        saved = True

    return JsonResponse({
        "status": "ok",
        "saved": saved,
    })

@require_POST
def upload_profile_image(request):
    player_name = request.POST.get("name")
    image = request.FILES.get("image")

    if not player_name or not image:
        return JsonResponse(
            {"error": "name and image are required"},
            status=400,
        )

    if image.size > MAX_PROFILE_IMAGE_SIZE:
        return JsonResponse(
            {"error": "image must be 10MB or smaller"},
            status=400,
        )

    extension = image.name.rsplit(".", 1)[-1].lower()
    if (
        "." not in image.name or
        extension not in ALLOWED_PROFILE_IMAGE_EXTENSIONS or
        image.content_type not in ALLOWED_PROFILE_IMAGE_TYPES
    ):
        return JsonResponse(
            {"error": "upload a JPG, PNG, GIF, or WEBP image"},
            status=400,
        )

    player, created = Player.objects.get_or_create(
        name=player_name
    )
    player.profile_image = image
    player.save(update_fields=["profile_image"])

    return JsonResponse({
        "status": "ok",
        "image_url": player.profile_image.url,
    })
