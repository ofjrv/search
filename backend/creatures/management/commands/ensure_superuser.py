import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "환경변수 DJANGO_SUPERUSER_USERNAME / PASSWORD / EMAIL로 슈퍼유저를 만들거나 "
        "비밀번호·권한을 다시 맞춘다 (배포 빌드용)"
    )

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()

        # 값이 없으면 경고만 하고 빌드는 계속
        if not username or not password:
            self.stderr.write(
                self.style.WARNING(
                    "경고: DJANGO_SUPERUSER_USERNAME 또는 DJANGO_SUPERUSER_PASSWORD가 비어 있어 "
                    "슈퍼유저를 만들지 않았어요."
                )
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            **{User.USERNAME_FIELD: username}, defaults={"email": email}
        )
        if email:
            user.email = email
        # 비밀번호·권한을 환경변수 기준으로 다시 맞춤 (비밀번호는 출력하지 않음)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        action = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"Superuser ready: {username} ({action})"))
