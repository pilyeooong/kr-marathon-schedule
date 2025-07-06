# Korean Marathon Schedule Scraper

[![PyPI version](https://badge.fury.io/py/kr-marathon-schedule.svg)](https://badge.fury.io/py/kr-marathon-schedule)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

국내 마라톤, 러닝 대회 스케줄 정보를 수집하고 제공하는 Python 패키지입니다.

## 설치

```bash
pip install kr-marathon-schedule
```

## 사용법

### 프로그래밍 방식

```python
from kr_marathon_schedule import get_marathons
from kr_marathon_schedule.scraper import MarathonScraper

# 현재 년도 마라톤 정보 가져오기 (상세 정보 포함)
marathons = get_marathons()
print(f"총 {len(marathons)}개의 마라톤 대회")

# 빠른 기본 정보만 수집 (상세 정보 제외)
marathons_basic = get_marathons(fetch_details=False)
print(f"총 {len(marathons_basic)}개의 마라톤 대회 (기본 정보만)")

# 특정 연도 지정
marathons_2024 = get_marathons("2024", fetch_details=False)

# MarathonScraper 직접 사용
scraper = MarathonScraper("2025", fetch_details=True)
data = scraper.scrape()

# 특정 이벤트 상세 정보 가져오기
detail = scraper.get_event_detail("40468")
print(f"상세 정보: {detail}")
```

### CLI 사용

```bash
# 기본 사용 (상세 정보 포함, JSON 형식)
kr-marathon-schedule

# 빠른 기본 정보만 수집 (상세 정보 제외)
kr-marathon-schedule --no-details

# CSV 형식으로 저장
kr-marathon-schedule --format csv --output ./data --verbose

# 특정 연도 지정 (기본 정보만)
kr-marathon-schedule --year 2024 --no-details

# 상세 정보 포함 (시간이 오래 걸림)
kr-marathon-schedule --year 2025 --verbose

# 도움말
kr-marathon-schedule --help
```

#### CLI 옵션

- `--year, -y`: 수집할 연도 지정 (기본값: 현재 연도)
- `--format, -f`: 출력 형식 (json, csv)
- `--output, -o`: 출력 디렉토리 (기본값: marathon_data)
- `--verbose, -v`: 상세 출력
- `--no-details`: 상세 정보 수집 제외 (빠른 실행)

## 데이터 형식

### 기본 정보 (--no-details 사용시)

```json
{
  "year": "2025",
  "date": "1/1",
  "month": 1,
  "day": 1,
  "day_of_week": "수",
  "event_name": "2025 선양맨몸마라톤",
  "tags": ["7km"],
  "location": "대전 엑스포과학공원 물빛광장",
  "organizer": ["(주)선양소주"],
  "phone": "042-580-1823"
}
```

### 상세 정보 포함 (기본 설정)

```json
{
  "year": "2025",
  "date": "1/1",
  "month": 1,
  "day": 1,
  "day_of_week": "수",
  "event_name": "2025 선양맨몸마라톤",
  "tags": ["7km"],
  "location": "대전 엑스포과학공원 물빛광장",
  "organizer": ["(주)선양소주"],
  "phone": "042-580-1823",
  "representative": "(주)선양소주",
  "email": "example@example.com",
  "start_time": "11:11",
  "registration_period": "2024년10월31일~2024년12월20일",
  "homepage": "http://www.djmmrun.co.kr/",
  "description": "대회 상세 설명...",
  "venue_detail": "상세 장소 정보"
}
```

### 추가된 상세 정보 필드

- `representative`: 대표자명
- `email`: 이메일 주소
- `start_time`: 출발시간
- `registration_period`: 접수기간
- `homepage`: 공식 홈페이지 URL
- `description`: 대회 소개 및 상세 정보
- `venue_detail`: 대회장 상세 정보

## 성능 및 사용 가이드

### 실행 시간

- **기본 정보만 수집** (`--no-details`): 약 5-10초
- **상세 정보 포함** (기본 설정): 약 3-5분 (300+ 이벤트)

### 권장 사용법

1. **빠른 목록 확인**: `--no-details` 옵션 사용
2. **상세 분석**: 전체 상세 정보 수집 또는 특정 이벤트만 선택적 수집
3. **정기 수집**: 기본 정보는 자주, 상세 정보는 주기적으로 수집

## 개발

```bash
git clone https://github.com/pilyeooong/kr-marathon-schedule.git
cd kr-marathon-schedule
pip install -e ".[dev]"
```

### 테스트 실행

```bash
python -m pytest tests/ -v
```

## 라이센스

MIT License

## 데이터 소스

https://raw.githubusercontent.com/pilyeooong/kr-marathon-schedule/refs/heads/master/marathon_data/latest-marathon-schedule.json
