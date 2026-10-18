from rest_framework import viewsets

from .models import Creature
from .serializers import CreatureSerializer


def squash(text):
    # 공백을 모두 지운 문자열
    return "".join((text or "").split())


class CreatureViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CreatureSerializer

    def get_queryset(self):
        return Creature.objects.filter(is_visible=True).order_by("name")

    def filter_queryset(self, queryset):
        if self.action != "list":
            return queryset

        # DB마다 정렬 규칙(collation)이 달라 PostgreSQL에서 가나다순이 깨짐
        # → 파이썬에서 정렬 (한글 음절은 유니코드 순서가 곧 가나다순)
        creatures = sorted(queryset, key=lambda c: c.name)
        q = squash(self.request.query_params.get("q"))
        if not q:
            return creatures

        # 데이터가 적어서 파이썬에서 공백 제거 후 비교
        matches = []
        for c in creatures:
            names = [squash(c.name)] + [squash(a) for a in c.aliases.split(",")]
            if any(q in n for n in names if n):
                matches.append(c)

        # 이름 정확히 일치 → 별칭 정확히 일치 → 나머지(가나다순 유지)
        def rank(c):
            if squash(c.name) == q:
                return 0
            if q in [squash(a) for a in c.aliases.split(",")]:
                return 1
            return 2

        return sorted(matches, key=rank)
