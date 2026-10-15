# 먹이를 찾아라 🔍

초등 4학년 과학 수업용 생물 검색 사이트입니다. 학생이 생물 이름을 검색하면 쉬운 설명과 먹이가 나옵니다.

- `backend/`: Django + Django REST Framework (API, 관리자 화면)
- `frontend/`: React (Vite) 검색 화면
- `먹이를찾아라_50종.csv`: 생물 데이터 (UTF-8 BOM)

---

## 1. 내 컴퓨터에서 실행하기

필요한 것: Python 3.12 이상, Node.js 20.19 이상

### 백엔드 (터미널 1)

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py import_creatures ../먹이를찾아라_50종.csv
python manage.py createsuperuser      # 관리자 계정 만들기 (처음 한 번)
python manage.py runserver
```

- API: http://127.0.0.1:8000/api/creatures/
- 관리자: http://127.0.0.1:8000/teacher-mukgi-2026/ (개발용 기본 주소, `/admin/`은 404)

> 내 컴퓨터용 개발 계정(`admin` / `mukbang-dev-1234`)은 **내 컴퓨터의 SQLite에서만** 씁니다.
> 배포 서버에는 절대 만들지 마세요. (아래 [6. 보안](#6-보안-학생이-운영자-화면을-찾지-못하게) 참고)

### 프론트엔드 (터미널 2)

```bash
cd frontend
npm install
npm run dev
```

- 검색 화면: http://localhost:5173/
- 백엔드 주소를 바꾸려면 `frontend/.env.local` 파일에 적습니다 (기본값 `http://127.0.0.1:8000`).

  ```
  VITE_API_URL=http://127.0.0.1:8000
  ```

> 같은 와이파이의 태블릿(디벗)으로 시험해 보려면: 백엔드는 `python manage.py runserver 0.0.0.0:8000`,
> 프론트엔드는 `npm run dev -- --host`로 켜고, `VITE_API_URL`과 백엔드의 `ALLOWED_HOSTS`·`CORS_ALLOWED_ORIGINS`에 내 컴퓨터 IP를 넣습니다.

### 테스트

```bash
cd backend
python manage.py test
```

---

## 2. API

모든 API는 관리자 화면에서 **보이기(is_visible)** 가 켜진 생물만 돌려줍니다.

| 주소 | 설명 |
| --- | --- |
| `GET /api/creatures/` | 전체 목록 (가나다순) |
| `GET /api/creatures/?q=개구리` | 이름 또는 다른 이름에 검색어가 들어간 생물. 공백은 무시하고, 이름이 정확히 같은 생물이 맨 앞 |
| `GET /api/creatures/<id>/` | 생물 하나의 자세한 정보 |

---

## 3. CSV 다시 불러오기

CSV를 고친 뒤 아래 명령을 다시 실행하면 됩니다. **이름**을 기준으로 있는 생물은 내용을 덮어쓰고, 없는 생물은 새로 추가합니다. 여러 번 실행해도 중복되지 않습니다.

```bash
cd backend
python manage.py import_creatures ../먹이를찾아라_50종.csv
```

- 관리자 화면에서 바꾼 **보이기** 설정은 다시 불러와도 유지됩니다.
- CSV에서 줄을 지워도 DB에서는 지워지지 않습니다. 학생에게 안 보이게 하려면 관리자 화면에서 **보이기**를 끄세요.
- CSV의 이름을 바꾸면 새 생물로 추가됩니다. 옛 이름은 관리자 화면에서 숨기거나 지우세요.
- CSV는 UTF-8(BOM 있어도 됨)로 저장해야 합니다. 엑셀에서는 "CSV UTF-8(쉼표로 분리)"로 저장하세요.

## 4. 관리자 화면에서 바로 고치기

http://127.0.0.1:8000/teacher-mukgi-2026/ → **생물** (배포 서버에서는 `ADMIN_PATH`로 정한 주소)

- 목록에서 **보이기** 체크를 끄고 아래 **저장** 버튼을 누르면 학생 화면에서 바로 사라집니다.
- 오른쪽 필터로 검수 상태·분류별로 볼 수 있고, 위 검색창으로 이름을 찾을 수 있습니다.
- 설명·먹이 문구를 관리자 화면에서 고쳤다면, CSV도 같이 고쳐 두세요. 다음에 CSV를 다시 불러오면 CSV 내용으로 덮어써집니다.

---

## 5. Render에 배포하기

백엔드는 **Web Service**, 프론트엔드는 **Static Site**, DB는 **PostgreSQL**로 만듭니다.
(Render의 디스크는 재배포 때 지워지므로 SQLite 대신 PostgreSQL을 씁니다.)

먼저 이 폴더 전체를 GitHub 저장소에 올립니다.

### 5-1. PostgreSQL

1. Render 대시보드 → **New → Postgres** 로 DB를 만듭니다.
2. 만든 DB의 **Internal Database URL**을 복사해 둡니다.

### 5-2. 백엔드 (Web Service)

**New → Web Service** → 저장소 선택 후:

| 항목 | 값 |
| --- | --- |
| Root Directory | `backend` |
| Runtime | Python 3 |
| Build Command | `./build.sh` |
| Start Command | `gunicorn config.wsgi:application` |

`build.sh`는 패키지 설치 → `collectstatic`(whitenoise가 admin 화면 CSS를 제공) → `migrate` → CSV 불러오기를 차례로 합니다.
(실행 권한 오류가 나면 Build Command를 `bash build.sh`로 바꾸세요.)

**Environment** 탭에 환경변수를 넣습니다.

| 이름 | 예시 값 | 설명 |
| --- | --- | --- |
| `DATABASE_URL` | (5-1에서 복사한 주소) | PostgreSQL 연결 |
| `SECRET_KEY` | (긴 무작위 문자열, "Generate" 버튼) | 꼭 새로 만들기 |
| `DEBUG` | `False` | 배포에서는 꼭 False (True면 오류 화면에 운영자 주소가 보임) |
| `ADMIN_PATH` | `kw8f3-mgr-q2zx7/` | 운영자 화면 주소. **추측하기 어려운 값**으로 새로 정하기 (아래 6번 참고) |
| `ALLOWED_HOSTS` | `mukbang-api.onrender.com` | 백엔드 주소(https:// 없이). Render 기본 주소는 자동으로 추가됨 |
| `CORS_ALLOWED_ORIGINS` | `https://mukbang.onrender.com` | 프론트엔드 주소. 여러 개면 쉼표로 구분, 끝에 `/` 없이 |
| `CSRF_TRUSTED_ORIGINS` | `https://mukbang-api.onrender.com` | 관리자 로그인용 (백엔드 주소, https:// 포함) |
| `PYTHON_VERSION` | `3.13.3` | 선택 |

배포가 끝나면 **Shell** 탭에서 관리자 계정을 **새로** 만듭니다.

```bash
python manage.py createsuperuser
```

- 개발용 계정(`admin` / `mukbang-dev-1234`)은 배포 서버에 **만들지 마세요.** 이 비밀번호는 README와 대화 기록에 남아 있어 안전하지 않습니다.
- 아이디는 `admin`처럼 흔한 이름을 피하고, 비밀번호는 **12자 이상**으로 다른 사이트에서 쓰지 않는 것으로 정하세요.
- 비밀번호는 학교 공용 PC에 저장하지 말고, 담당 선생님만 알고 있도록 합니다.

### 5-3. 프론트엔드 (Static Site)

**New → Static Site** → 같은 저장소 선택 후:

| 항목 | 값 |
| --- | --- |
| Root Directory | `frontend` |
| Build Command | `npm install && npm run build` |
| Publish Directory | `dist` |
| 환경변수 `VITE_API_URL` | `https://mukbang-api.onrender.com` (백엔드 주소) |

`VITE_API_URL`은 빌드할 때 들어가므로, 바꾼 뒤에는 **다시 배포**해야 합니다.

### 5-4. 배포 확인

1. `https://(백엔드주소)/api/creatures/` 에서 50종이 보이는지
2. `https://(백엔드주소)/(ADMIN_PATH)/` 에 로그인되는지 (CSS가 깨지지 않는지), `https://(백엔드주소)/admin/` 은 404인지
3. 프론트엔드 주소에서 "메뚜기"를 검색해 카드가 나오는지

> 무료 요금제 Web Service는 한동안 접속이 없으면 잠들어서, 첫 검색이 30초~1분 걸릴 수 있습니다.
> 수업 시작 전에 미리 사이트를 한 번 열어 두세요.

---

## 6. 보안: 학생이 운영자 화면을 찾지 못하게

| 장치 | 내용 |
| --- | --- |
| 숨긴 운영자 주소 | 운영자 화면은 환경변수 `ADMIN_PATH` 주소에만 있습니다 (개발 기본값 `teacher-mukgi-2026/`). `/admin/`으로 들어오면 404가 납니다. |
| 프론트엔드에 링크 없음 | 학생 화면(React) 어디에도 운영자 주소나 링크가 없습니다. 앞으로도 넣지 마세요. |
| JSON만 응답 | 배포(`DEBUG=False`)에서는 DRF 개발자 화면을 끄고 API가 JSON만 돌려줍니다. |
| 로그인 잠금 (django-axes) | 같은 아이디·같은 IP로 비밀번호를 **5번** 틀리면 **15분** 동안 로그인이 막힙니다. |

### 운영자 주소 정하기

- Render 환경변수 `ADMIN_PATH`에 아무도 추측할 수 없는 값을 넣습니다. 예를 들어 아래 명령으로 만든 값 뒤에 `/`를 붙이면 됩니다.

  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(12))"
  ```

- 학교·선생님 이름, 연도처럼 짐작하기 쉬운 단어는 피하세요. 개발 기본값 `teacher-mukgi-2026/`는 배포에서 쓰지 마세요.
- 주소는 즐겨찾기에만 저장하고, 수업 화면을 띄운 상태(전자칠판·화면 공유)에서는 열지 마세요.
- 주소가 학생에게 알려졌다면 `ADMIN_PATH` 값만 바꾸고 다시 배포하면 됩니다.

### 로그인이 잠겼을 때

15분을 기다리거나, Render **Shell** 탭에서 바로 풀 수 있습니다.

```bash
python manage.py axes_reset                       # 잠금 모두 풀기
python manage.py axes_reset_username <아이디>     # 특정 아이디만 풀기
```

> 학교에서는 학생과 선생님이 같은 인터넷 주소(IP)를 쓰는 경우가 많습니다.
> 그래서 IP만으로 잠그지 않고 **아이디+IP 조합**으로 잠급니다. 학생이 다른 아이디로 장난을 쳐도 선생님 계정은 막히지 않습니다.
