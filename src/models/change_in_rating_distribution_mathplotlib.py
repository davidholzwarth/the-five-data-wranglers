import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
from src.utils.evaluation_utils import CB_color_cycle 

# Define rating buckets for readability
rating_buckets = np.arange(0, 5.5, 0.5)


def rating_evolution_over_time(
    df,
    df_name,
    path,
    bucket=rating_buckets,
    min_ratings=1000,
    colors=CB_color_cycle ,
):

    # changes unix timestamp to date
    df["datetime"] = df["date"].apply(datetime.datetime.fromtimestamp)
    df["year"] = df["datetime"].dt.strftime("%Y")

    # Clean and process the DataFrame
    df_cleaned = df.dropna(subset=["rating"])
    df_cleaned["rating"] = df_cleaned["rating"].astype(float)

    # Apply rating buckets
    df_cleaned["rating_buckets"] = pd.cut(
        df_cleaned["rating"], bins=bucket, right=False, include_lowest=True
    )

    # Calculate the total number of ratings per year
    ratings_count = df_cleaned.groupby("year").size()

    # Filter for years with more than `min_ratings` ratings
    filtered_years = ratings_count[ratings_count > min_ratings].index
    df_filtered = df_cleaned[df_cleaned["year"].isin(filtered_years)]

    # Calculate distribution of ratings per filtered year
    grouped = df_filtered.groupby(["year", "rating_buckets"], observed=False).size()
    percentage_df = (
        grouped.groupby(level=0).apply(lambda x: x / x.sum()).unstack(fill_value=0)
    )

    # Recalculate the ratings count for filtered years
    ratings_count_filtered = ratings_count[ratings_count > min_ratings]

    # Plot the stacked bar chart with the secondary y-axis
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Primary y-axis for stacked bar chart (distribution of ratings)
    percentage_df.plot(kind="bar", stacked=True, ax=ax1, color=colors, width=0.8)
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Relative distribution of ratings")
    ax1.set_title(f"Distribution of ratings for " + df_name)
    ax1.legend(title="Rating Interval", bbox_to_anchor=(1.1, 1), loc="upper left")

    # Secondary y-axis for the count of ratings
    ax2 = ax1.twinx()  # Creates a secondary y-axis
    ratings_count_filtered.plot(
        kind="line",
        ax=ax2,
        color="black",
        marker="o",
        linewidth=2,
        label="Total Ratings",
    )
    ax2.set_ylabel("Total number of ratings")
    ax2.legend(loc="upper left")

    # Customize x-axis
    ax1.set_xticks(range(len(ratings_count_filtered.index)))
    ax1.set_xticklabels(ratings_count_filtered.index, rotation=45)

    fig.savefig(path, bbox_inches="tight")


# Function for filtering and diplaying the change in reviewers rating over time
def rating_evolution_with_rating_number(
    df,
    df_name,
    path,
    colors=CB_color_cycle,
    bucket=rating_buckets,
    nr_reviews=200,
):
    # Cleaning and merging dataframes
    df_cleaned = df.dropna(subset=["rating"])[1:]
    df_cleaned["rating"] = df_cleaned["rating"].astype(
        float
    )  # tranforms all ratings to int
    df_cleaned[["user_id", "rating", "date"]].drop_duplicates()

    # Sorts the DataFrame by user and date to ensure correct order of ratings and adds column for rating number for respective user
    df_sorted = df_cleaned.sort_values(by=["user_id", "date"])
    df_sorted["rating_order"] = df_sorted.groupby("user_id").cumcount() + 1

    # Uses a cutoff for amount of ratings, applies buckets to dataframe and calculates distribution
    df_filtered = df_sorted[df_sorted["rating_order"] <= nr_reviews].copy()
    df_filtered["rating_buckets"] = pd.cut(
        df_filtered["rating"], bins=bucket, right=False, include_lowest=True
    )
    df_amount = (
        df_filtered.groupby(["rating_order", "rating_buckets"], observed=False)
        .size()
        .reset_index(name="count")
    )
    df_amount["percentage"] = df_amount.groupby("rating_order")["count"].transform(
        lambda x: x / x.sum()
    )

    # Pivots the data for stacked bar plot
    pivot_df = df_amount.pivot(
        index="rating_order", columns="rating_buckets", values="percentage"
    ).fillna(0)

    # Create the plot with two y-axes
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # First plot (stacked bar plot for relative distribution)
    pivot_df.plot(kind="bar", stacked=True, ax=ax1, color=colors)
    ax1.set_xlabel("Rating number")
    ax1.set_ylabel("Relative distribution of ratings")
    ax1.set_title("Relative Distribution of ratings by Rating number for " + df_name)
    ax1.set_xticks(np.arange(0, nr_reviews, 10), np.arange(0, nr_reviews, 10))
    custom_legend_labels = [
        f"{bucket[i]} - {bucket[i+1]}" for i in range(len(bucket) - 1)
    ]
    ax1.legend(
        title="Rating interval",
        labels=custom_legend_labels,
        bbox_to_anchor=(1.1, 1),
        loc="upper left",
    )

    ax2 = ax1.twinx()
    # Aggregate the total number of responses for each rating order
    response_count = df_sorted.groupby("rating_order")["user_id"].count()
    ax2.plot(
        np.arange(0, len(response_count), 1),
        response_count.values,
        color="black",
        linestyle="-",
        label="Number of Reviews",
    )
    ax2.set_ylabel("Number of ratings")
    ax2.legend(loc="upper left")
    fig.savefig(path, bbox_inches="tight")
