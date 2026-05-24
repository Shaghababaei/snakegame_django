from django.urls import path
from . import views

urlpatterns = [
    path("",views.play,name="play"),
    path("api/submit_score/",views.submit_score,name="submit_score"),
    path("api/upload_profile_image/",views.upload_profile_image,name="upload_profile_image"),
    path("leaderboard/",views.leaderboard,name ="leaderboard"),
]
