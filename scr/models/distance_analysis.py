import os
from time import sleep

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from geopy.distance import geodesic as GD
from geopy.geocoders import Nominatim
from src.utils.evaluation_utils import US_STATES_CODES

import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'


def join_users_breweries_ratings(df_users, df_breweries, df_ratings, ratebeer=True):
    """
    Join the user, breweries and ratings dataframes
    :param df_user: the user dataframe
    :param df_breweries: the breweries dataframe
    :param df_ratings: the ratings dataframe
    :return: a merged dataframe
    """
    df_breweries.rename(columns={"id": "brewery_id"}, inplace=True)
    if ratebeer:
        df_users.dropna(subset="user_name", inplace=True)
        df_ratings.dropna(subset="user_name", inplace=True)

        df_ratings = df_ratings.convert_dtypes()
        df_users = df_users.convert_dtypes()
        df_users["user_name"] = df_users["user_name"].astype(str)
        df_ratings["user_name"] = df_ratings["user_name"].astype(str)

        df_joined = df_ratings.merge(
            df_users, on="user_name", how="left", suffixes=["_ratings", "_users"]
        )

    else:
        df_ratings = df_ratings.convert_dtypes()
        df_users = df_users.convert_dtypes()
        df_joined = df_ratings.merge(
            df_users, on="user_id", how="left", suffixes=["_ratings", "_users"]
        )
    df_joined = df_joined.merge(
        df_breweries,
        on="brewery_id",
        how="inner",
        suffixes=["_joined", "_breweries"],
    )

    df_joined.dropna(subset=["location"], inplace=True)
    df_joined["brewery_location"] = df_joined["brewery_location"].apply(
        remove_html_tags
    )
    return df_joined


def remove_html_tags(value: str):
    return value.split("<")[0]


def retrieve_location_data(df_ba_joined, df_rb_joined):

    if os.path.exists("data/locations.csv"):
        df_locations = pd.read_csv("data/locations.csv")
    else:
        geolocator = Nominatim(user_agent="beer_ratings")
        latitudes = []
        longitudes = []
        locations = []

        ba_locations = set(df_ba_joined["location"].unique()).union(
            df_ba_joined["brewery_location"].unique()
        )
        rb_locations = set(df_rb_joined["location"].unique()).union(
            df_rb_joined["brewery_location"].unique()
        )
        all_locations = ba_locations.union(rb_locations)
        print("Total locations: {}".format(len(all_locations)))

        for location in list(all_locations):
            sleep(1)  # Only one query per second is allowed by the API
            try:
                geo_info = geolocator.geocode(location)
                latitudes.append(geo_info.latitude)
                longitudes.append(geo_info.longitude)
                locations.append(location)
                print(
                    location,
                    "information fetched:",
                    str(geo_info),
                    "(",
                    geo_info.latitude,
                    geo_info.longitude,
                    ")",
                )
            except:
                latitudes.append(np.nan)
                longitudes.append(np.nan)
                locations.append(location)
                print("Error fetching information for", location)

        df_locations = pd.DataFrame(
            {"location": locations, "latitude": latitudes, "longitude": longitudes}
        )
        df_locations.sort_index(inplace=True)
        df_locations.to_csv("data/locations.csv", index=False)
    return df_locations


def translate_locations(joined_df, df_locations):
    """Translates locations into longitutde and latitude coordinates."""
    joined_df["longitude_user"] = joined_df["location"].map(
        df_locations.set_index("location")["longitude"].to_dict()
    )
    joined_df["latitude_user"] = joined_df["location"].map(
        df_locations.set_index("location")["latitude"].to_dict()
    )
    joined_df["longitude_brewery"] = joined_df["brewery_location"].map(
        df_locations.set_index("location")["longitude"].to_dict()
    )
    joined_df["latitude_brewery"] = joined_df["brewery_location"].map(
        df_locations.set_index("location")["latitude"].to_dict()
    )
    return joined_df


def calculate_distances(joined_df, df_locations):
    """Calculates the distances between users and breweries."""
    joined_df = translate_locations(joined_df, df_locations)
    joined_df["distance_user_brewery"] = haversine_distance(
        joined_df[["latitude_user", "longitude_user"]].values,
        joined_df[["latitude_brewery", "longitude_brewery"]].values,
    )
    return joined_df


def haversine_distance(origin, destination):
    """Calculates the haversine distance between two points from their latitudes and longitudes.

    Args:
        origin (tuple): Longitude and latitude of the origin point.
        destination (tuple): Longitude and latitude of the destination point.

    Returns:
        float: distance between the two points in kilometers.
    """
    lat1, lon1 = origin[:, 0], origin[:, 1]
    lat2, lon2 = destination[:, 0], destination[:, 1]
    radius = 6371  # km

    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) * np.sin(dlat / 2) + np.cos(np.radians(lat1)) * np.cos(
        np.radians(lat2)
    ) * np.sin(dlon / 2) * np.sin(dlon / 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    d = radius * c

    return d


def plot_distance_ratings(
    joined_df, ratebeer=True, max_distance=15000, bucket_per_distance=250
):
    """Plots the distance between users and breweries against the ratings given by the users."""
    if ratebeer:
        user_column = "user_name"
    else:
        user_column = "user_id"
    df_name = "RateBeer" if ratebeer else "BeerAdvocate"

    # Colors for plotting
    colors = [
        "blue",
        "red",
        "purple",
        "brown",
        "hotpink",
        "cyan",
        "gold",
        "darkgreen",
        "violet",
        "chocolate",
    ]

    # Rating buckets to make the plot more readable
    rating_buckets = np.arange(0, 5.5, 0.5)

    # Cleaning and merging dataframes
    df_cleaned = joined_df.dropna(subset=["rating"])[1:]
    df_cleaned["rating"] = df_cleaned["rating"].astype(
        float
    )  # tranforms all ratings to int
    df_cleaned[[user_column, "rating", "date"]].drop_duplicates()

    # Uses a cutoff for distance between brewery and reviewer, applies buckets to dataframe and calculates distribution
    df_filtered = df_cleaned[df_cleaned["distance_user_brewery"] <= max_distance]
    df_filtered["rating_buckets"] = pd.cut(
        df_filtered["rating"], bins=rating_buckets, right=False, include_lowest=True
    )
    df_filtered["distance_user_brewery_buckets"] = pd.cut(
        df_filtered["distance_user_brewery"],
        bins=np.arange(0, max_distance + 1, bucket_per_distance),
        right=True,
        include_lowest=True,
        labels=np.arange(0, max_distance, bucket_per_distance),
    )
    df_amount = (
        df_filtered.groupby(
            ["distance_user_brewery_buckets", "rating_buckets"], observed=False
        )
        .size()
        .reset_index(name="count")
    )
    df_amount["percentage"] = df_amount.groupby(
        "distance_user_brewery_buckets", observed=False
    )["count"].transform(lambda x: x / x.sum())

    # Pivots the data for stacked bar plot
    pivot_df = df_amount.pivot(
        index="distance_user_brewery_buckets",
        columns="rating_buckets",
        values="percentage",
    ).fillna(0)

    # Create the plot with two y-axes
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # First plot (stacked bar plot for relative distribution)
    pivot_df.plot(kind="bar", stacked=True, ax=ax1, color=colors)
    ax1.set_xlabel("Distance between user and brewery [km]")
    ax1.set_ylabel("Relative distribution of ratings")
    ax1.set_title("Relative Distribution of ratings by Rating number for " + df_name)
    # ax1.set_xticks(np.arange(0, max_distance, bucket_per_distance), np.arange(0, max_distance, bucket_per_distance))
    custom_legend_labels = [
        f"{rating_buckets[i]} - {rating_buckets[i+1]}"
        for i in range(len(rating_buckets) - 1)
    ]
    ax1.legend(
        title="Rating interval",
        labels=custom_legend_labels,
        bbox_to_anchor=(1.1, 1),
        loc="upper left",
    )

    ax2 = ax1.twinx()

    # Aggregate the total number of responses for each rating order
    response_count = df_filtered.groupby(
        "distance_user_brewery_buckets", observed=False
    )[user_column].count()
    ax2.plot(
        np.arange(0, len(response_count), 1),
        response_count.values,
        color="black",
        linestyle="-",
        label="Number of Reviews",
    )
    ax2.set_yscale("log")
    ax2.set_ylabel("Number of ratings")
    ax2.legend(loc="upper right")
    plt.show()
