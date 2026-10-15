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


class EnsureSuperuserTests(TestCase):
    def run_cmd(self, **env):
        import os
        from io import StringIO
        from unittest import mock

        from django.core.management import call_command

        out, err = StringIO(), StringIO()
        keys = ["DJANGO_SUPERUSER_USERNAME", "DJANGO_SUPERUSER_PASSWORD", "DJANGO_SUPERUSER_EMAIL"]
        clean = {k: v for k, v in os.environ.items() if k not in keys}
        with mock.patch.dict(os.environ, {**clean, **env}, clear=True):
            call_command("ensure_superuser", stdout=out, stderr=err)
        return out.getvalue(), err.getvalue()

    def test_creates_then_resets(self):
        from django.contrib.auth.models import User

        out, _ = self.run_cmd(DJANGO_SUPERUSER_USERNAME="teacher", DJANGO_SUPERUSER_PASSWORD="first-Pass-123")
        self.assertIn("Superuser ready: teacher", out)
        self.assertNotIn("first-Pass-123", out)

        # 권한을 뺏고 비밀번호를 바꾼 뒤 다시 실행하면 복구
        User.objects.filter(username="teacher").update(is_staff=False, is_superuser=False)
        out, _ = self.run_cmd(DJANGO_SUPERUSER_USERNAME="teacher", DJANGO_SUPERUSER_PASSWORD="second-Pass-456")
        self.assertNotIn("second-Pass-456", out)
        user = User.objects.get(username="teacher")
        self.assertTrue(user.is_staff and user.is_superuser)
        self.assertTrue(user.check_password("second-Pass-456"))
        self.assertEqual(User.objects.count(), 1)

    def test_missing_env_only_warns(self):
        from django.contrib.auth.models import User

        out, err = self.run_cmd()
        self.assertIn("경고", err)
        self.assertEqual(User.objects.count(), 0)
