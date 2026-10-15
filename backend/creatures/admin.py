from django.contrib import admin

from .models import Creature


@admin.register(Creature)
class CreatureAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "review_status", "is_visible")
    list_editable = ("is_visible",)  # 목록에서 바로 숨기기/보이기
    list_filter = ("review_status", "category", "is_visible")
    search_fields = ("name", "aliases")
    list_per_page = 100
