import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Define rating buckets for readability
rating_buckets = np.arange(0, 5.5, 0.5)

def rating_evolution_over_time(
    df,
    df_name,
    bucket=rating_buckets,
    min_ratings=1000,
):
    
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
    
    # Count the occurrences of each combination of year and rating_buckets
    counts = df_filtered.groupby(["year", "rating_buckets"], observed=False).size().reset_index(name="count")

    # Calculate percentages directly
    counts["percentage"] = counts.groupby("year")["count"].transform(lambda x: x / x.sum())

    # Reshape the DataFrame to have rating_buckets as columns
    percentage_df = counts.pivot_table(
        index="year",
        columns="rating_buckets",
        values="percentage",
        fill_value=0,
        observed=False
    ).reset_index()
    
    # Clean up column names
    percentage_df.columns.name = None  # Remove the pivot table's column name
    name = df_name.split(" ")
    
    melted_df = percentage_df.melt(id_vars="year", var_name="rating_bucket", value_name="percentage")
    fig = px.bar(
        melted_df,
        x="year",
        y="percentage",
        color="rating_bucket",
        title=f"Rating Distribution over Time for {name[0]} {name[1]}",
        labels={"percentage": "Percentage", "year": "Year", "rating_bucket": "Rating Bucket"},
    )

    fig.update_layout(barmode="stack", bargap=0)
    fig.write_html(f"src/plots/rating_evolution_over_time_{name[0]}_{name[1]}.html", include_plotlyjs="cdn")


def rating_evolution_with_rating_number(
    df,
    df_name,
    bucket=rating_buckets,
    nr_reviews=300,
):
    # Cleaning and merging dataframes
    df_cleaned = df.dropna(subset=["rating"])[1:]
    df_cleaned["rating"] = df_cleaned["rating"].astype(
        float
    )

    # Sorts the DataFrame by user and date to ensure correct order of ratings and adds column for rating number for respective user
    df_sorted = df_cleaned.sort_values(by=["user_id", "date"])
    df_sorted["rating_order"] = df_sorted.groupby("user_id").cumcount() + 1

    # Uses a cutoff for amount of ratings, applies buckets to dataframe and calculates distribution
    df_filtered = df_sorted[df_sorted["rating_order"] <= nr_reviews]

    df_filtered["rating_buckets"]= pd.cut(
        df_filtered["rating"], bins=bucket, right=False, include_lowest=True
    ).copy()
    
    df_amount = (
        df_filtered.groupby(["rating_order", "rating_buckets"], observed=False)
        .size()
        .reset_index(name="count")
    )
    df_amount["percentage"] = df_amount.groupby("rating_order")["count"].transform(
        lambda x: x / x.sum()
    )

    # Pivots the data for stacked bar plot
    pivot_df = df_amount.pivot_table(
        index="rating_order", 
        columns="rating_buckets", 
        values="percentage", 
        fill_value=0,
        observed=False
    ).reset_index()
    
    # Clean up column names
    pivot_df.columns.name = None 
    
    name = df_name.split(" ") 
    
    melted_df = pivot_df.melt(id_vars="rating_order", var_name="rating_bucket", value_name="percentage")
    fig = px.bar(
        melted_df,
        x="rating_order",
        y="percentage",
        color="rating_bucket",
        title=f"Relative Distribution of Ratings Given Rating Number for {name[0]} {name[1]}",
        labels={"percentage": "Percentage", "rating_order": "Rating Number", "rating_bucket": "Rating Bucket"},
    )
    fig.update_layout(barmode="stack", bargap=0)
    fig.write_html(f"src/plots/rating_evolution_given_amount_of_ratings_{name[0]}_{name[1]}.html", include_plotlyjs="cdn")