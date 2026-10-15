import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from creatures.models import Creature

# CSV 컬럼 → 모델 필드
COLUMNS = {
    "다른 이름(검색용)": "aliases",
    "분류": "category",
    "설명": "description",
    "먹이": "food",
    "검수 상태": "review_status",
    "출처 기관": "source_org",
    "출처 링크": "source_url",
    "메모": "memo",
}


class Command(BaseCommand):
    help = "CSV 파일의 생물 데이터를 불러온다 (이름 기준 덮어쓰기, 여러 번 실행해도 중복 없음)"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", help="CSV 파일 경로 (UTF-8 / UTF-8 BOM)")

    @transaction.atomic
    def handle(self, *args, **options):
        path = options["csv_path"]
        try:
            # utf-8-sig: BOM이 있어도 없어도 읽힘
            with open(path, encoding="utf-8-sig", newline="") as f:
                rows = list(csv.DictReader(f))
        except FileNotFoundError:
            raise CommandError(f"파일을 찾을 수 없어요: {path}")

        missing = {"이름", *COLUMNS} - set(rows[0].keys() if rows else [])
        if missing:
            raise CommandError(f"CSV에 없는 컬럼: {', '.join(sorted(missing))}")

        valid_status = set(Creature.ReviewStatus.values)
        created = updated = 0
        for line, row in enumerate(rows, start=2):
            name = row["이름"].strip()
            if not name:
                continue
            # 글자 내용은 그대로, 앞뒤 공백만 정리
            data = {field: (row[col] or "").strip() for col, field in COLUMNS.items()}
            # 별칭은 쉼표 주변 공백 정리
            data["aliases"] = ",".join(
                a.strip() for a in data["aliases"].split(",") if a.strip()
            )
            if data["review_status"] not in valid_status:
                raise CommandError(
                    f"{line}번째 줄 '{name}': 검수 상태 값이 이상해요 ({data['review_status']})"
                )
            # is_visible은 건드리지 않음 (관리자가 숨긴 설정 유지)
            _, is_new = Creature.objects.update_or_create(name=name, defaults=data)
            created += is_new
            updated += not is_new

        self.stdout.write(
            self.style.SUCCESS(
                f"완료: 새로 추가 {created}개, 업데이트 {updated}개 (전체 {Creature.objects.count()}개)"
            )
        )
