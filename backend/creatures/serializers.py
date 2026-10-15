from rest_framework import serializers

from .models import Creature


class CreatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creature
        # 메모·보이기 여부는 학생 화면에 내보내지 않음
        fields = [
            "id",
            "name",
            "aliases",
            "category",
            "description",
            "food",
            "review_status",
            "source_org",
            "source_url",
        ]
