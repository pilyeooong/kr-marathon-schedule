# Korean Marathon Schedule Scraper

국내 마라톤·러닝 대회 일정을 [roadrun.co.kr](http://www.roadrun.co.kr/schedule/list.php)에서 수집해 JSON으로 저장하는 스크립트입니다. 러닝 캘린더 앱이 이 저장소의 JSON을 읽습니다.

## 실행

```bash
pip install -r requirements.txt
python scrap.py              # 목록 + 대회별 상세 페이지까지 수집
python scrap.py --no-detail  # 목록 페이지만 수집(빠름)
```

올해와 다음 해 대회를 수집합니다(연도는 실행 시점 기준으로 자동으로 정해집니다).

## 출력

`marathon_data/`에 세 종류의 파일을 씁니다.

- `latest-marathon-schedule.json` — 가장 최근 수집 전체(올해 + 다음 해)
- `<연도>_latest-marathon-schedule.json` — 연도별 최근 수집
- `<YYYYMMDDHHMMSS>-marathon-schedule.json` — 실행할 때마다 남는 기록

## 자동 갱신

`.github/workflows/scrape.yml`이 매일 정기 실행(`cron: '0 1 * * *'`, UTC)과 수동 실행(`workflow_dispatch`)으로 `python scrap.py`를 돌리고, `marathon_data/`가 바뀌었으면 커밋·push합니다.

## 데이터 형식

대회 하나의 예(상세 수집 포함):

```json
{
  "year": "2026",
  "date": "1/1",
  "month": 1,
  "day": 1,
  "day_of_week": "목",
  "event_name": "2026 새해 일출런",
  "tags": ["10km", "5km"],
  "location": "신정교하부육상트랙구장",
  "organizer": ["(사)대한생활체육마라톤협회"],
  "phone": "00-1644-4219",
  "event_id": "41182",
  "homepage": "http://...",
  "email": "...",
  "representative": "...",
  "start_time": "09:00",
  "region": "서울",
  "venue_detail": "신정교하부육상트랙구장",
  "registration_period": "2025년11월6일~2025년12월15일",
  "description": "...",
  "latitude": 37.5178604,
  "longitude": 126.8819583,
  "map_address": "서울특별시 영등포구 영등포로2길 62"
}
```

`--no-detail`로 실행하면 목록 페이지에서 얻는 `year`~`event_id`·`homepage`·`email`만 들어갑니다. `event_id`·`homepage`·`email`과 상세 필드(`representative`부터 `map_address`까지)는 원문에 값이 없으면 빠질 수 있습니다.

## 데이터 주소

- 대회 일정: https://raw.githubusercontent.com/pilyeooong/kr-marathon-schedule/refs/heads/master/marathon_data/latest-marathon-schedule.json
- 앱 버전 체크: https://raw.githubusercontent.com/pilyeooong/kr-marathon-schedule/refs/heads/master/app-config/version-check.json

## 라이선스

MIT License
