import argparse
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from pybaseballstats.statcast import statcast_date_range_pitch_by_pitch
from pybaseballstats.utils.statcast_utils import STATCAST_YEAR_RANGES


class StatcastBenchmark:
    def __init__(self, results_dir="tests/benchmark_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.results_file = self.results_dir / "benchmark_results.json"
        self.benchmark_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Load previous results if they exist
        self.all_results = {}
        if self.results_file.exists():
            with open(self.results_file, "r") as f:
                self.all_results = json.load(f)

    def generate_date_ranges(self, year=2023):
        """Generate test date ranges of different lengths using STATCAST_YEAR_RANGES for consistency"""
        if year not in STATCAST_YEAR_RANGES:
            print(
                f"Year {year} not in STATCAST_YEAR_RANGES, using latest available year"
            )
            year = max(STATCAST_YEAR_RANGES.keys())

        season_start, season_end = STATCAST_YEAR_RANGES[year]

        # Format dates as strings
        def format_date(d):
            return d.strftime("%Y-%m-%d")

        # Calculate date ranges within the season
        total_days = (season_end - season_start).days
        one_day = timedelta(days=1)
        one_week = timedelta(days=7)
        two_weeks = timedelta(days=14)
        one_month = timedelta(days=30)
        three_months = timedelta(days=90)

        date_ranges = [
            # Small ranges
            (
                "1_day",
                format_date(season_start),
                format_date(min(season_start + one_day, season_end)),
            ),
            (
                "1_week",
                format_date(season_start),
                format_date(min(season_start + one_week, season_end)),
            ),
            (
                "2_weeks",
                format_date(season_start),
                format_date(min(season_start + two_weeks, season_end)),
            ),
            (
                "1_month",
                format_date(season_start),
                format_date(min(season_start + one_month, season_end)),
            ),
        ]

        # Only add larger ranges if the season is long enough
        if total_days > 90:
            date_ranges.append(
                (
                    "3_months",
                    format_date(season_start),
                    format_date(min(season_start + three_months, season_end)),
                )
            )

        # Add half-season if season is long enough
        if total_days > 60:
            half_season = timedelta(days=total_days // 2)
            date_ranges.append(
                (
                    "half_season",
                    format_date(season_start),
                    format_date(season_start + half_season),
                )
            )

        # Add full season
        date_ranges.append(
            (
                f"full_{year}_season",
                format_date(season_start),
                format_date(season_end),
            )
        )

        available_years = sorted(STATCAST_YEAR_RANGES.keys())
        year_index = available_years.index(year) if year in available_years else -1

        # Add 3-year test if we have at least 3 years of data
        if year_index >= 2:  # Need current year plus 2 previous years
            three_years_ago = available_years[year_index - 2]
            three_years_start, _ = STATCAST_YEAR_RANGES[three_years_ago]
            date_ranges.append(
                (
                    f"3_year_test_{three_years_ago}_to_{year}",
                    format_date(three_years_start),
                    format_date(season_end),
                )
            )

        # Add 10-year test if we have at least 10 years of data
        if year_index >= 9:  # Need current year plus 9 previous years
            ten_years_ago = available_years[year_index - 9]
            ten_years_start, _ = STATCAST_YEAR_RANGES[ten_years_ago]
            date_ranges.append(
                (
                    f"10_year_test_{ten_years_ago}_to_{year}",
                    format_date(ten_years_start),
                    format_date(season_end),
                )
            )

        return date_ranges

    def run_benchmark(self, date_ranges=None, year=2023, note=""):
        """Run benchmarks for all date ranges"""
        if date_ranges is None:
            date_ranges = self.generate_date_ranges(year)

        results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": note,
            "year": year,
            "ranges": {},
        }

        for range_name, start_date, end_date in date_ranges:
            print(f"Testing range: {range_name} ({start_date} to {end_date})")
            total_days = (
                datetime.strptime(end_date, "%Y-%m-%d")
                - datetime.strptime(start_date, "%Y-%m-%d")
            ).days
            print(f"Total days: {total_days}")
            # Measure execution time
            start_time = time.time()
            try:
                df = statcast_date_range_pitch_by_pitch(start_date, end_date)
                success = True
                row_count = len(df.collect())
            except Exception as e:
                success = False
                row_count = 0
                print(f"Error during benchmark: {e}")

            end_time = time.time()
            execution_time = end_time - start_time

            # Store results
            results["ranges"][range_name] = {
                "start_date": start_date,
                "end_date": end_date,
                "execution_time": execution_time,
                "success": success,
                "row_count": row_count,
                "data_to_time_ratio": row_count / execution_time if success else None,
            }

            print(f"  Time: {execution_time:.2f} seconds, Rows: {row_count}")

        # Save results
        self.all_results[self.benchmark_id] = results
        with open(self.results_file, "w") as f:
            json.dump(self.all_results, f, indent=2)

        return results

    def compare_results(self, benchmark_ids=None, save_chart=True):
        """Compare results between different benchmark runs"""
        if not self.all_results:
            print("No benchmark results available.")
            return

        if benchmark_ids is None:
            # Use the most recent benchmarks (up to 5)
            benchmark_ids = list(self.all_results.keys())[-5:]

        # Extract data for comparison
        comparison_data = {}
        for benchmark_id in benchmark_ids:
            if benchmark_id in self.all_results:
                data = self.all_results[benchmark_id]
                label = f"{benchmark_id}"
                if data.get("note"):
                    label += f" ({data['note']})"

                comparison_data[label] = {
                    range_name: results["execution_time"]
                    for range_name, results in data["ranges"].items()
                    if results["success"]
                }

        # Create DataFrame for comparison
        df = pd.DataFrame(comparison_data)

        # Print tabular comparison
        print("\nBenchmark Comparison (execution time in seconds):")
        print(df)

        # Calculate improvement percentages if there are multiple benchmarks
        if len(comparison_data) > 1:
            first_benchmark = list(comparison_data.keys())[0]
            last_benchmark = list(comparison_data.keys())[-1]

            improvement = {}
            for range_name in df.index:
                if range_name in df.index:
                    first_time = df.loc[range_name, first_benchmark]
                    last_time = df.loc[range_name, last_benchmark]
                    if first_time > 0:
                        pct_change = ((first_time - last_time) / first_time) * 100
                        improvement[range_name] = pct_change

            if improvement:
                print("\nPerformance Improvement (first vs. last benchmark):")
                for range_name, pct in improvement.items():
                    print(
                        f"  {range_name}: {pct:.2f}% {'faster' if pct > 0 else 'slower'}"
                    )

        # Create and save chart
        if save_chart:
            plt.figure(figsize=(12, 8))
            ax = df.plot(kind="bar", figsize=(12, 8))
            plt.title("Execution Time Comparison")
            plt.ylabel("Time (seconds)")
            plt.xlabel("Date Range")
            plt.xticks(rotation=45)
            plt.grid(axis="y", linestyle="--", alpha=0.7)

            # Add values on top of bars
            for container in ax.containers:
                ax.bar_label(container, fmt="%.1f", padding=3)

            plt.tight_layout()
            chart_path = (
                self.results_dir
                / f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            plt.savefig(chart_path)
            print(f"\nChart saved to: {chart_path}")
            plt.close()

        return df


def main():
    parser = argparse.ArgumentParser(description="Benchmark Statcast functions")
    parser.add_argument("--run", action="store_true", help="Run a new benchmark")
    parser.add_argument(
        "--compare",
        nargs="*",
        help="Compare specific benchmark IDs or latest if none provided",
    )
    parser.add_argument(
        "--note", type=str, default="", help="Note for this benchmark run"
    )
    parser.add_argument(
        "--list", action="store_true", help="List all available benchmark IDs"
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2024,
        help="Season year to use for date ranges (default: 2024)",
    )

    args = parser.parse_args()
    benchmark = StatcastBenchmark()

    if args.list:
        if not benchmark.all_results:
            print("No benchmark results available.")
        else:
            print("Available benchmark IDs:")
            for bid, data in benchmark.all_results.items():
                note = f" - {data['note']}" if data.get("note") else ""
                print(f"  {bid}{note} ({data['timestamp']})")

    if args.run:
        print(f"Running benchmark with note: {args.note} for year: {args.year}")
        benchmark.run_benchmark(year=args.year, note=args.note)

    if args.compare is not None:
        benchmark.compare_results(args.compare if args.compare else None)


if __name__ == "__main__":
    main()
