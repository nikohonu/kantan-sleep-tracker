import datetime as dt
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


import click
from rich.console import Console

console = Console()
print = console.print
data_file = Path.home() / "data" / "sleep.csv"


@click.group()
def cli():
    pass


def prompt_datetime(name, default):
    year = click.prompt(f"Enter {name} date. Year", default=default.year)
    month = click.prompt("Month", default=default.month)
    day = click.prompt("Day", default=default.day)
    hours = click.prompt("Hours", type=click.IntRange(0, 24))
    minutes = click.prompt("Minutes", type=click.IntRange(0, 60))
    datetime = dt.datetime(year, month, day, hours, minutes, 0)
    return datetime


@cli.command()
@click.option(
    "--start",
    type=click.DateTime(formats=["%Y-%m-%dT%H:%M"]),
)
@click.option(
    "--end",
    type=click.DateTime(formats=["%Y-%m-%dT%H:%M"]),
)
@click.option("--score", type=click.IntRange(1, 3), prompt=True)
def add(start, end, score):
    start = (
        start
        if start
        else prompt_datetime("start", dt.datetime.now() - dt.timedelta(days=1))
    )
    end = end if end else prompt_datetime("end", dt.datetime.now())
    print(start, end, end - start, end)
    if data_file.exists():
        df = pd.read_csv(data_file)
    else:
        df = pd.DataFrame(columns=["start", "end", "score"])
    df.loc[len(df)] = [start, end, score]
    df.to_csv(data_file, index=False)


@cli.command()
def stats():
    if data_file.exists():
        df = pd.read_csv(data_file)
    else:
        df = pd.DataFrame(columns=["start", "end", "score"])
    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])
    df["duration"] = df["end"] - df["start"]
    df["end hour"] = df["end"].dt.hour + (df["end"].dt.minute / 60)
    df["duration"] = df["duration"].dt.total_seconds() / 60 / 60
    df['average'] = df['duration'].rolling(window=2).mean()
    print(df)
    result = df.groupby('duration')['score'].mean()
    plot = result.plot(x="duration", y="score")
    plot.set_title("Score vs Duration")
    plot.set_xlabel("duration")
    plot.set_ylabel("score")
    print(result)
    plt.show()
    result = df.groupby('end hour')['score'].mean()
    plot = result.plot(x="end hour", y="score")
    plot.set_title("Score vs End Hour")
    plot.set_xlabel("end hour")
    plot.set_ylabel("score")
    print(result)
    plt.show()
    result = df.groupby('average')['score'].mean()
    plot = result.plot(x="average", y="score")
    plot.set_title("Score vs average")
    plot.set_xlabel("averagev")
    plot.set_ylabel("score")
    print(result)
    plt.show()


def main():
    cli()
