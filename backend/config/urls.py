from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from creatures.views import CreatureViewSet

router = DefaultRouter()
router.register("creatures", CreatureViewSet, basename="creature")

admin.site.site_header = "먹이 관계 알아보기 관리"
admin.site.site_title = "먹이 관계 알아보기 관리"

urlpatterns = [
    # 운영자 주소는 환경변수 ADMIN_PATH로만 정함 (/admin/ 은 404)
    path(settings.ADMIN_PATH, admin.site.urls),
    path("api/", include(router.urls)),
]
