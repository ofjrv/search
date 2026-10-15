from django.db import models


class Creature(models.Model):
    """검색 대상 생물 한 종."""

    class ReviewStatus(models.TextChoices):
        OFFICIAL = "공식 확인", "공식 확인"
        PARTIAL = "일부 확인", "일부 확인"
        UNVERIFIED = "미확인", "미확인"

    name = models.CharField("이름", max_length=50, unique=True)
    aliases = models.CharField(
        "다른 이름", max_length=200, blank=True, help_text="쉼표로 구분 (예: 참개구리,논개구리)"
    )
    category = models.CharField("분류", max_length=30)
    description = models.TextField("설명")
    food = models.TextField("먹이", help_text='식물이면 "X"')
    review_status = models.CharField(
        "검수 상태",
        max_length=10,
        choices=ReviewStatus.choices,
        default=ReviewStatus.UNVERIFIED,
    )
    source_org = models.CharField("출처 기관", max_length=200, blank=True)
    source_url = models.URLField("출처 링크", max_length=500, blank=True)
    memo = models.TextField("메모", blank=True)
    is_visible = models.BooleanField("보이기", default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "생물"
        verbose_name_plural = "생물"

    def __str__(self):
        return self.name
