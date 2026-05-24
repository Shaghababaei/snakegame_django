from django.db.models import OuterRef, Subquery
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from .serializers import (
    ApiErrorSerializer,
    LeaderboardUserSerializer,
    ProfileImageResponseSerializer,
    ProfileImageUploadRequestSerializer,
    ProfileImageUploadResponseSerializer,
    ScoreSubmissionRequestSerializer,
    ScoreSubmissionResponseSerializer,
)
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


def get_best_scores(limit=None):
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
        .order_by("-points", "-created_at")
    )
    if limit is not None:
        scores = scores[:limit]
    return scores


def serialize_leaderboard_score(request, score):
    profile_image = None
    if score.player.profile_image:
        profile_image = request.build_absolute_uri(score.player.profile_image.url)

    return {
        "id": score.player.id,
        "name": score.player.name,
        "points": score.points,
        "profile_image": profile_image,
    }


# Create your views here.
def leaderboard(request):
    scores = get_best_scores(10)
    return render(request,"game/leaderboard.html",{"scores" : scores})

def play(request):
    return render(request,"game/play.html")


@extend_schema(
    responses={
        200: LeaderboardUserSerializer(many=True),
    },
)
@api_view(["GET"])
def leaderboard_api(request):
    users = [
        serialize_leaderboard_score(request, score)
        for score in get_best_scores(3)
    ]

    return Response(users)


@extend_schema(
    responses={
        200: LeaderboardUserSerializer(many=True),
    },
)
@api_view(["GET"])
def leaderboard_all_api(request):
    users = [
        serialize_leaderboard_score(request, score)
        for score in get_best_scores()
    ]
    return Response(users)


@extend_schema(
    responses={
        200: ProfileImageResponseSerializer,
        404: ApiErrorSerializer,
    },
)
@api_view(["GET"])
def profile_image_api(request, player_id):
    player = Player.objects.filter(pk=player_id).first()
    if player is None:
        return Response(
            {"error": "user not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not player.profile_image:
        return Response({
            "id": player.id,
            "name": player.name,
            "profile_image": None,
            "message": "user has not image profile yet",
        })

    return Response({
        "id": player.id,
        "name": player.name,
        "profile_image": request.build_absolute_uri(player.profile_image.url),
    })


@extend_schema(
    request=ScoreSubmissionRequestSerializer,
    responses={
        200: ScoreSubmissionResponseSerializer,
        400: ApiErrorSerializer,
    },
)
@api_view(["POST"])
@parser_classes([JSONParser])
def submit_score(request):

    player_name = request.data.get("name")
    points = request.data.get("points")

    if not player_name or points is None:
        return Response(
            {"error": "name and points are required"},
            status=status.HTTP_400_BAD_REQUEST,
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

    return Response({
        "status": "ok",
        "saved": saved,
    })

@extend_schema(
    request=ProfileImageUploadRequestSerializer,
    responses={
        200: ProfileImageUploadResponseSerializer,
        400: ApiErrorSerializer,
    },
)
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_profile_image(request):
    player_name = request.data.get("name")
    image = request.FILES.get("image")

    if not player_name or not image:
        return Response(
            {"error": "name and image are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if image.size > MAX_PROFILE_IMAGE_SIZE:
        return Response(
            {"error": "image must be 10MB or smaller"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    extension = image.name.rsplit(".", 1)[-1].lower()
    if (
        "." not in image.name or
        extension not in ALLOWED_PROFILE_IMAGE_EXTENSIONS or
        image.content_type not in ALLOWED_PROFILE_IMAGE_TYPES
    ):
        return Response(
            {"error": "upload a JPG, PNG, GIF, or WEBP image"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    player, created = Player.objects.get_or_create(
        name=player_name
    )
    player.profile_image = image
    player.save(update_fields=["profile_image"])

    return Response({
        "status": "ok",
        "image_url": player.profile_image.url,
    })
