"""물류 수작업일보 이미지 생성 - 메인 실행"""
import argparse
from datetime import date, datetime
from pathlib import Path

from sample_data import generate_daily_report_data
from report_generator import generate_report_image


def main():
    parser = argparse.ArgumentParser(description="물류 수작업일보 이미지 생성기")
    parser.add_argument(
        "--date", "-d",
        type=str,
        default=None,
        help="보고 날짜 (YYYY-MM-DD). 기본값: 오늘",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="출력 파일 경로. 기본값: output/manual_report_YYYY-MM-DD.png",
    )
    args = parser.parse_args()

    if args.date:
        report_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    else:
        report_date = date.today()

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    if args.output:
        output_path = args.output
    else:
        output_path = str(output_dir / f"manual_report_{report_date}.png")

    print(f"[*] 보고 날짜: {report_date}")
    data = generate_daily_report_data(report_date)
    print(f"[*] 데이터 생성 완료 (총 수작업: {data['total_manual_today']:,} 건)")

    result = generate_report_image(data, output_path)
    print(f"[+] 일보 이미지 생성 완료: {result}")


if __name__ == "__main__":
    main()
