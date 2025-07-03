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

# 현재 년도 마라톤 정보 가져오기
marathons = get_marathons()
print(f"총 {len(marathons)}개의 마라톤 대회")

# 특정 연도 지정
marathons_2024 = get_marathons("2024")
```

### CLI 사용

```bash
# 기본 사용 (JSON 형식)
kr-marathon-schedule

# CSV 형식으로 저장
kr-marathon-schedule --format csv --output ./data --verbose

# 특정 연도 지정
kr-marathon-schedule --year 2024

# 도움말
kr-marathon-schedule --help
```

## 데이터 형식

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

## 개발

```bash
git clone https://github.com/yourusername/kr-marathon-schedule.git
cd kr-marathon-schedule
pip install -e .
```

## 라이센스

MIT License

## 데이터 소스

https://raw.githubusercontent.com/pilyeooong/kr-marathon-schedule/refs/heads/master/marathon_data/latest-marathon-schedule.json
