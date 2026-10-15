from django.conf import settings
from django.test import TestCase

from .models import Creature


class CreatureApiTests(TestCase):
    def setUp(self):
        mk = Creature.objects.create
        mk(name="개구리", aliases="참개구리,논개구리", category="양서류", description="d", food="f")
        mk(name="청개구리", category="양서류", description="d", food="f")
        mk(name="메뚜기", aliases="벼메뚜기", category="곤충", description="d", food="f")
        mk(name="숨김", category="곤충", description="d", food="f", is_visible=False)

    def names(self, url):
        return [c["name"] for c in self.client.get(url).json()]

    def test_list_sorted_and_visible_only(self):
        self.assertEqual(self.names("/api/creatures/"), ["개구리", "메뚜기", "청개구리"])

    def test_exact_name_first(self):
        self.assertEqual(self.names("/api/creatures/?q=개구리"), ["개구리", "청개구리"])

    def test_alias_and_spaces(self):
        self.assertEqual(self.names("/api/creatures/?q=참 개구리"), ["개구리"])
        self.assertEqual(self.names("/api/creatures/?q= 메 뚜 기 "), ["메뚜기"])

    def test_hidden_not_returned(self):
        hidden = Creature.objects.get(name="숨김")
        self.assertEqual(self.names("/api/creatures/?q=숨김"), [])
        self.assertEqual(self.client.get(f"/api/creatures/{hidden.id}/").status_code, 404)


class SecurityTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User

        User.objects.create_superuser("teacher", "t@example.com", "correct-horse-battery")
        self.login_url = f"/{settings.ADMIN_PATH}login/"

    def test_default_admin_path_is_404(self):
        self.assertEqual(self.client.get("/admin/").status_code, 404)
        self.assertEqual(self.client.get("/admin/login/").status_code, 404)

    def test_secret_admin_path_shows_login(self):
        res = self.client.get(f"/{settings.ADMIN_PATH}", follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.redirect_chain[-1][0], f"{self.login_url}?next=/{settings.ADMIN_PATH}")

    def login(self, password):
        return self.client.post(self.login_url, {"username": "teacher", "password": password})

    def test_lockout_after_5_failures(self):
        for _ in range(4):
            self.assertEqual(self.login("wrong").status_code, 200)  # 로그인 화면 다시
        self.assertEqual(self.login("wrong").status_code, 429)  # 5번째에 잠김
        # 잠긴 동안은 맞는 비밀번호도 막힘
        self.assertEqual(self.login("correct-horse-battery").status_code, 429)
