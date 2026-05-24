from django.contrib import admin
from .models import Player, Score

# Register your models here.
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ["id","name"]

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ["id","player","points","created_at"]
    list_filter = ["created_at"]
    search_fields = ["player__name"]