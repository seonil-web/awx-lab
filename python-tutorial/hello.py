#사용자 이름을 입력받아 인사하는 간단한 프로그램을 만들어줘
name = input("이름을 입력하세요: ")
print(f"안녕하세요, {name}님!")
#입력이 비어있으면 'guest'로 처리하고, test 함수도 함께 작성해줘
def greet_user(name):
    if not name.strip():
        name = "guest"
    return f"안녕하세요, {name}님!"
#표준입출력 사용
if __name__ == "__main__":
    user_name = input("이름을 입력하세요: ")
    print(greet_user(user_name))

"""
숫자 리스트를 표준입출력으로 받아 평균(average)과 최댓값(max)을 출력합니다.

사용법 예:
  - 파이프 입력:
      echo "1 2 3 4.5" | python stats.py
      echo "1,2,3,4.5" | python stats.py

  - 상호작용 입력 (터미널에서 실행 시):
      python stats.py
      # 프롬프트에 숫자들을 공백 또는 쉼표로 구분하여 입력

옵션:
  --avg / --no-avg    평균 출력 여부 (기본: 출력)
  --max / --no-max    최댓값 출력 여부 (기본: 출력)
  --precision N       소수점 자리수 (기본: 3)
"""
import sys
import argparse

def parse_numbers(text):
    if not text:
        return []
    # 쉼표를 공백으로 바꿔 여러 구분자 지원
    tokens = text.replace(",", " ").split()
    nums = []
    for t in tokens:
        try:
            nums.append(float(t))
        except ValueError:
            raise ValueError(f"유효하지 않은 숫자: '{t}'")
    return nums

def read_from_stdin_or_prompt():
    # 파이프/리다이렉트된 입력이 있는지 확인
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    # 터미널에서 직접 실행한 경우 프롬프트
    try:
        return input("숫자들을 공백 또는 쉼표로 구분하여 입력하세요: ").strip()
    except EOFError:
        return ""

def main():
    parser = argparse.ArgumentParser(description="표준입출력으로 숫자 리스트를 받아 평균/최댓값을 출력합니다.")
    parser.add_argument("--no-avg", dest="do_avg", action="store_false", help="평균을 출력하지 않음")
    parser.add_argument("--no-max", dest="do_max", action="store_false", help="최댓값을 출력하지 않음")
    parser.add_argument("--precision", type=int, default=3, help="출력 소수점 자리수 (기본 3)")
    args = parser.parse_args()

    raw = read_from_stdin_or_prompt()
    try:
        numbers = parse_numbers(raw)
    except ValueError as e:
        print(f"입력 오류: {e}", file=sys.stderr)
        sys.exit(1)

    if not numbers:
        print("오류: 숫자가 입력되지 않았습니다.", file=sys.stderr)
        sys.exit(1)

    if args.do_avg:
        avg = sum(numbers) / len(numbers)
        print(f"평균: {avg:.{args.precision}f}")
    if args.do_max:
        m = max(numbers)
        print(f"최댓값: {m:.{args.precision}f}")

if __name__ == "__main__":
    main()



import argparse
import csv
from collections import defaultdict
from datetime import datetime
import random
import sys
import os

import matplotlib.pyplot as plt

DATE_FORMATS = ["%Y-%m-%d", "%Y/%m/%d", "%Y-%m", "%Y-%m-%dT%H:%M:%S"]

def parse_date(s):
    s = s.strip()
    # 허용되는 간단한 변형 처리
    if len(s) == 7 and "-" in s:  # "YYYY-MM" 형태
        s = s + "-01"
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"날짜 형식 인식 실패: '{s}' (예: 2023-05-17)")

def read_csv_aggregate_by_month(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    agg = defaultdict(float)
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # 기대되는 컬럼: date, revenue (대소문자 혼합 허용)
        headers = {h.lower(): h for h in reader.fieldnames or []}
        if "date" not in headers or "revenue" not in headers:
            raise ValueError("CSV에 'date'와 'revenue' 컬럼이 필요합니다.")
        for row in reader:
            try:
                dt = parse_date(row[headers["date"]])
                rev = float(row[headers["revenue"]])
                key = dt.strftime("%Y-%m")  # 월 단위 키
                agg[key] += rev
            except Exception as e:
                raise ValueError(f"CSV 파싱 중 오류: {e}")
    if not agg:
        raise ValueError("CSV에 매출 데이터가 없습니다.")
    # 정렬된 (월, 합계) 리스트 반환
    items = sorted(agg.items(), key=lambda kv: datetime.strptime(kv[0] + "-01", "%Y-%m-%d"))
    months, totals = zip(*items)
    return months, totals

def generate_sample_csv(path, start_year=2024, months=12):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "revenue"])
        for m in range(months):
            y = start_year + (m // 12)
            mo = (m % 12) + 1
            # 각 월에 임의의 일자를 넣고 매출을 랜덤 생성
            day = random.randint(1, 28)
            date = f"{y:04d}-{mo:02d}-{day:02d}"
            revenue = round(random.uniform(5000, 50000), 2)
            writer.writerow([date, revenue])
    return path

def plot_bar(months, totals, out_path=None, show=False, title="월별 매출 합계"):
    plt.style.use("seaborn-darkgrid")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(months, totals, color="#4c72b0")
    ax.set_xlabel("월")
    ax.set_ylabel("매출 합계")
    ax.set_title(title)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    if out_path:
        fig.savefig(out_path)
        print(f"그래프를 저장했습니다: {out_path}")
    if show:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description="CSV를 읽어 월별 매출 합계를 막대그래프로 그립니다.")
    parser.add_argument("--csv", "-c", help="입력 CSV 파일 경로 (date,revenue 컬럼 필요)")
    parser.add_argument("--sample", "-s", nargs="?", const="sample_revenue.csv", help="샘플 CSV 생성 (옵션으로 파일명 지정)")
    parser.add_argument("--out", "-o", default="revenue_by_month.png", help="출력 이미지 파일 경로 (기본 revenue_by_month.png)")
    parser.add_argument("--show", action="store_true", help="그래프를 화면에 표시")
    args = parser.parse_args()

    try:
        csv_path = args.csv
        if args.sample:
            csv_path = generate_sample_csv(args.sample)
            print(f"샘플 CSV 생성됨: {csv_path}")

        if not csv_path:
            parser.error("입력 CSV가 없습니다. --csv PATH 또는 --sample 를 사용하세요.")

        months, totals = read_csv_aggregate_by_month(csv_path)
        plot_bar(months, totals, out_path=args.out, show=args.show)
    except Exception as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

import argparse
import csv
from collections import defaultdict
from datetime import datetime
import os
import random
import sys

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

DATE_FORMATS = ["%Y-%m-%d", "%Y/%m/%d", "%Y-%m", "%Y-%m-%dT%H:%M:%S"]

def parse_date(s):
    s = (s or "").strip()
    if not s:
        raise ValueError("빈 날짜값")
    if len(s) == 7 and "-" in s:
        s = s + "-01"
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"날짜 형식 인식 실패: '{s}'")

def read_csv_aggregate_by_month(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    agg = defaultdict(float)
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV에 헤더가 없습니다.")
        headers = {h.lower(): h for h in reader.fieldnames}
        if "date" not in headers or "revenue" not in headers:
            raise ValueError("CSV에 'date'와 'revenue' 컬럼이 필요합니다.")
        for row in reader:
            try:
                dt = parse_date(row[headers["date"]])
                rev = float((row[headers["revenue"]] or "").replace(",", ""))
            except Exception as e:
                raise ValueError(f"CSV 파싱 오류: {e}")
            key = dt.strftime("%Y-%m")
            agg[key] += rev
    if not agg:
        return [], []
    items = sorted(agg.items(), key=lambda kv: datetime.strptime(kv[0] + "-01", "%Y-%m-%d"))
    months, totals = zip(*items)
    return list(months), list(totals)

def generate_sample_csv(path, start_year=2024, months=12):
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "revenue"])
        for m in range(months):
            y = start_year + (m // 12)
            mo = (m % 12) + 1
            day = random.randint(1, 28)
            date = f"{y:04d}-{mo:02d}-{day:02d}"
            revenue = round(random.uniform(1000, 50000), 2)
            writer.writerow([date, revenue])
    return path

def print_monthly_summary(months, totals, out_stream=sys.stdout):
    if not months:
        print("매출 데이터가 없습니다.", file=out_stream)
        return
    for mo, tot in zip(months, totals):
        print(f"{mo}: {tot:.2f}", file=out_stream)

def plot_monthly(months, totals, out_path=None, show=True, title="월별 매출 합계"):
    if plt is None:
        raise RuntimeError("matplotlib이 설치되어 있지 않습니다.")
    if not months:
        print("플롯할 매출 데이터가 없습니다.")
        return
    plt.style.use("seaborn-darkgrid")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(months, totals, color="#4c72b0")
    ax.set_xlabel("월")
    ax.set_ylabel("매출 합계")
    ax.set_title(title)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    if out_path:
        fig.savefig(out_path)
        print(f"그래프를 저장했습니다: {out_path}")
    if show:
        plt.show()

def main():
    default_csv = os.path.join("c:\\", "projects", "python-tutorial", "sales.csv")
    parser = argparse.ArgumentParser(description="sales.csv를 읽어 월별 합계를 출력합니다. 파일 없으면 샘플 생성.")
    parser.add_argument("--csv", "-c", default=default_csv, help="입력 CSV 파일 경로")
    parser.add_argument("--generate-sample", "-g", action="store_true", help="샘플 CSV 생성")
    parser.add_argument("--sample-file", "-s", help="샘플 생성 파일명 (예: -s c:\\path\\sample.csv)")
    parser.add_argument("--plot", action="store_true", help="월별 막대그래프를 그립니다 (matplotlib 필요)")
    parser.add_argument("--out", "-o", help="그래프 저장 경로 (--plot 함께 사용)")
    args = parser.parse_args()

    csv_path = args.csv

    if args.generate_sample:
        target = args.sample_file or csv_path
        try:
            csv_path = generate_sample_csv(target)
            print(f"샘플 CSV 생성됨: {csv_path}")
        except Exception as e:
            print(f"샘플 생성 실패: {e}", file=sys.stderr)
            sys.exit(1)
    elif not os.path.exists(csv_path):
        try:
            csv_path = generate_sample_csv(csv_path)
            print(f"입력 파일이 없어 샘플을 생성했습니다: {csv_path}")
        except Exception as e:
            print(f"샘플 생성 실패: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        months, totals = read_csv_aggregate_by_month(csv_path)
    except Exception as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)

    print_monthly_summary(months, totals)

    if args.plot:
        try:
            plot_monthly(months, totals, out_path=args.out, show=True)
        except Exception as e:
            print(f"그래프 생성 오류: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()