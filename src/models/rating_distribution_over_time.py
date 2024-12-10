import pandas as pd
import datetime
import numpy as np
import plotly.graph_objects as go

# Define rating buckets for readability
rating_buckets = np.arange(0, 5.5, 0.5)

def rating_evolution_over_time(
    df,
    df_name,
    bucket=rating_buckets,
    min_ratings=1000,
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

    # Create the stacked bar chart
    fig = go.Figure()
    for column in percentage_df.columns:
        fig.add_trace(
            go.Bar(
                name=str(column),
                x=percentage_df.index,
                y=percentage_df[column],
                hovertemplate=f"Rating Bucket: {column}<br>Percentage: {{y:.2%}}<extra></extra>",
            )
        )

    # Add the line chart for total ratings
    fig.add_trace(
        go.Scatter(
            name="Total Ratings",
            x=ratings_count_filtered.index,
            y=ratings_count_filtered.values,
            mode="lines+markers",
            line=dict(color="black", width=2),
            marker=dict(symbol="circle", size=8),
            yaxis="y2",
            hovertemplate="Year: %{x}<br>Total Ratings: %{y}<extra></extra>",
        )
    )

    # Layout adjustments
    fig.update_layout(
        barmode="stack",
        title=f"Distribution of ratings for {df_name}",
        xaxis=dict(title="Year"),
        yaxis=dict(title="Relative Distribution of Ratings", tickformat=".0%"),
        yaxis2=dict(
            title="Total Number of Ratings",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(title="Rating Interval"),
        template="plotly_white",
    )

    name = df_name.split(" ")
    fig.write_html(f"src/plots/rating_evolution_over_time_{name[0]}_{name[1]}.html", include_plotlyjs="cdn")


def rating_evolution_with_rating_number(
    df,
    df_name,
    bucket=rating_buckets,
    nr_reviews=300,
):
    # Cleaning and merging dataframes
    df_cleaned = df.dropna(subset=["rating"])[1:]
    df_cleaned["rating"] = df_cleaned["rating"].astype(float)
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

    # Aggregate the total number of responses for each rating order
    response_count = df_sorted.groupby("rating_order")["user_id"].count()

    # Create the stacked bar chart
    fig = go.Figure()
    for column in pivot_df.columns:
        fig.add_trace(
            go.Bar(
                name=str(column),
                x=pivot_df.index,
                y=pivot_df[column],
                hovertemplate=f"Rating Bucket: {column}<br>Percentage: {{y:.2%}}<extra></extra>",
            )
        )

    # Add the line chart for total responses
    fig.add_trace(
        go.Scatter(
            name="Number of Responses",
            x=response_count.index,
            y=response_count.values,
            mode="lines+markers",
            line=dict(color="black", width=2),
            marker=dict(symbol="circle", size=8),
            yaxis="y2",
            hovertemplate="Rating Order: %{x}<br>Total Responses: %{y}<extra></extra>",
        )
    )

    # Layout adjustments
    fig.update_layout(
        barmode="stack",
        title=f"Relative Distribution of Ratings by Rating Number for {df_name}",
        xaxis=dict(title="Rating Number"),
        yaxis=dict(title="Relative Distribution of Ratings", tickformat=".0%"),
        yaxis2=dict(
            title="Number of Ratings",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(title="Rating Interval"),
        template="plotly_white",
    )

    name = df_name.split(" ")
    fig.write_html(f"src/plots/rating_evolution_with_rating_number_{name[0]}_{name[1]}.html", include_plotlyjs="cdn")
