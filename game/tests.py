from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Player, Score


class ScoreSubmissionTests(TestCase):
    def setUp(self):
        self.client = Client()

    def submit_score(self, name, points):
        return self.client.post(
            reverse("submit_score"),
            data={"name": name, "points": points},
            content_type="application/json",
        )

    def test_only_player_top_score_is_saved(self):
        first_response = self.submit_score("Ada", 30)
        lower_response = self.submit_score("Ada", 10)
        higher_response = self.submit_score("Ada", 50)

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(lower_response.status_code, 200)
        self.assertEqual(higher_response.status_code, 200)

        player = Player.objects.get(name="Ada")
        scores = list(player.scores.values_list("points", flat=True))

        self.assertEqual(scores, [50])
        self.assertTrue(first_response.json()["saved"])
        self.assertFalse(lower_response.json()["saved"])
        self.assertTrue(higher_response.json()["saved"])

    def test_leaderboard_shows_one_best_score_per_player(self):
        ada = Player.objects.create(name="Ada")
        grace = Player.objects.create(name="Grace")
        Score.objects.create(player=ada, points=20)
        Score.objects.create(player=ada, points=80)
        Score.objects.create(player=grace, points=60)

        response = self.client.get(reverse("leaderboard"))

        self.assertEqual(response.status_code, 200)
        scores = list(response.context["scores"])
        self.assertEqual([score.player.name for score in scores], ["Ada", "Grace"])
        self.assertEqual([score.points for score in scores], [80, 60])

    def test_leaderboard_uses_saved_profile_image_url(self):
        image = SimpleUploadedFile(
            "avatar.png",
            b"fake-image-bytes",
            content_type="image/png",
        )
        upload_response = self.client.post(
            reverse("upload_profile_image"),
            data={"name": "Ada", "image": image},
        )

        self.assertEqual(upload_response.status_code, 200)

        player = Player.objects.get(name="Ada")
        Score.objects.create(player=player, points=40)

        response = self.client.get(reverse("leaderboard"))

        self.assertContains(response, 'src="/media/profiles/')
        self.assertContains(response, 'alt="Ada profile image"')
