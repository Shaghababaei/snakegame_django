from django.db import models

# Create your models here.
class Player(models.Model):
    name = models.CharField(max_length=100,unique=True)
    
    def __str__(self):
        return self.name
    
class Score(models.Model):
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="scores"
    )
    points = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-points","-created_at"]
    def __str__(self):
        return f"{self.player.name} - {self.points}"