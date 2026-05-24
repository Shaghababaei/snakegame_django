from django.urls import path
from . import views

urlpatterns = [
    path("",views.play,name="play"),
    path("api/leaderboard/",views.leaderboard_api,name="leaderboard_api"),
    path("api/leaderboard/all/",views.leaderboard_all_api,name="leaderboard_all_api"),
    path("api/users/<int:player_id>/profile_image/",views.profile_image_api,name="profile_image_api"),
    path("api/submit_score/",views.submit_score,name="submit_score"),
    path("api/upload_profile_image/",views.upload_profile_image,name="upload_profile_image"),
    path("leaderboard/",views.leaderboard,name ="leaderboard"),
]
