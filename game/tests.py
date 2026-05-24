import json

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

    def test_leaderboard_api_returns_top_three_users_with_profile_images(self):
        players = [
            Player.objects.create(name="Ada", profile_image="profiles/ada.png"),
            Player.objects.create(name="Grace", profile_image="profiles/grace.png"),
            Player.objects.create(name="Linus"),
            Player.objects.create(name="Dennis", profile_image="profiles/dennis.png"),
        ]
        Score.objects.create(player=players[0], points=80)
        Score.objects.create(player=players[1], points=120)
        Score.objects.create(player=players[2], points=60)
        Score.objects.create(player=players[3], points=40)

        response = self.client.get(reverse("leaderboard_api"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 3)
        self.assertEqual(
            [(user["id"], user["name"], user["points"]) for user in data],
            [
                (players[1].id, "Grace", 120),
                (players[0].id, "Ada", 80),
                (players[2].id, "Linus", 60),
            ],
        )
        self.assertEqual(
            data[0]["profile_image"],
            "http://testserver/media/profiles/grace.png",
        )
        self.assertEqual(
            data[1]["profile_image"],
            "http://testserver/media/profiles/ada.png",
        )
        self.assertIsNone(data[2]["profile_image"])

    def test_leaderboard_all_api_returns_all_leaderboard_records(self):
        players = [
            Player.objects.create(name="Ada"),
            Player.objects.create(name="Grace"),
            Player.objects.create(name="Linus"),
            Player.objects.create(name="Dennis"),
        ]
        Score.objects.create(player=players[0], points=80)
        Score.objects.create(player=players[1], points=120)
        Score.objects.create(player=players[2], points=60)
        Score.objects.create(player=players[3], points=40)

        response = self.client.get(reverse("leaderboard_all_api"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 4)
        self.assertEqual(
            [(user["name"], user["points"]) for user in data],
            [
                ("Grace", 120),
                ("Ada", 80),
                ("Linus", 60),
                ("Dennis", 40),
            ],
        )

    def test_profile_image_api_returns_user_profile_image(self):
        player = Player.objects.create(
            name="Ada",
            profile_image="profiles/ada.png",
        )

        response = self.client.get(
            reverse("profile_image_api", kwargs={"player_id": player.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "id": player.id,
            "name": "Ada",
            "profile_image": "http://testserver/media/profiles/ada.png",
        })

    def test_profile_image_api_returns_message_when_user_has_no_image(self):
        player = Player.objects.create(name="Ada")

        response = self.client.get(
            reverse("profile_image_api", kwargs={"player_id": player.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "id": player.id,
            "name": "Ada",
            "profile_image": None,
            "message": "user has not image profile yet",
        })

    def test_profile_image_api_returns_404_when_user_does_not_exist(self):
        response = self.client.get(
            reverse("profile_image_api", kwargs={"player_id": 999})
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "user not found"})

    def test_openapi_schema_documents_game_api_paths(self):
        response = self.client.get(reverse("schema"), HTTP_ACCEPT="application/json")

        self.assertEqual(response.status_code, 200)
        schema = json.loads(response.content)
        self.assertEqual(schema["openapi"], "3.0.3")
        self.assertIn("/api/leaderboard/", schema["paths"])
        self.assertIn("/api/leaderboard/all/", schema["paths"])
        self.assertIn("/api/users/{player_id}/profile_image/", schema["paths"])
        self.assertIn("/api/submit_score/", schema["paths"])
        self.assertIn("/api/upload_profile_image/", schema["paths"])

    def test_swagger_ui_route_loads_schema(self):
        response = self.client.get(reverse("swagger-ui"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SwaggerUIBundle")
        self.assertContains(response, reverse("schema"))
