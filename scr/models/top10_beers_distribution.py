import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

experience_threshold = 15  # Can be changed. Defines experience


def top10beers_ratings(df_ratings, df_nb_ratings, df_name):
    # Selecting the wanted columns and creating new df for ratings:
    filtered_ratings_df = pd.DataFrame(
        {
            "user_id": df_ratings["user_id"],
            "user_name": df_ratings["user_name"],
            "ratings": df_ratings["rating"],
            "beer_id": df_ratings["beer_id"],
            "beer_name": df_ratings["beer_name"],
        }
    )

    # And new df for the reviewers to have the number of given ratings per reviewer
    users_df = pd.DataFrame(
        {
            "nb_ratings": df_nb_ratings["nbr_ratings"],
            "user_id": df_nb_ratings["user_id"],
        }
    )

    # Merging the ratings with their respective BA or RB users_df via the 'user_id' column
    filtered_ratings_df = pd.merge(users_df, filtered_ratings_df, on="user_id")

    # Classifying by the number of reviews given per beer
    valuecount = pd.DataFrame(
        filtered_ratings_df["beer_name"].value_counts().reset_index()
    )
    valuecount.columns = ["beer_name", "count"]

    # Saving the 10 most reviewed beers
    top_10_beers = valuecount.head(10)

    # Selecting the rows from the BA or RB ratings that match with the Top_10 BA or RB respectively
    top10_ratings_df = filtered_ratings_df[
        filtered_ratings_df["beer_name"].isin(top_10_beers["beer_name"])
    ]

    # Sharing the Top10_ratings between experienced and new reviewers. The experience_threshold is used as separation

    top10_ratings_df.insert(5, "Experience", "Experienced")

    top10_ratings_df.loc[
        top10_ratings_df["nb_ratings"] < experience_threshold, "Experience"
    ] = "New"

    top10_ratings_copy_df = top10_ratings_df.copy(deep=True)
    top10_ratings_copy_df["Experience"] = "All"
    top10_ratings_df = pd.concat([top10_ratings_df, top10_ratings_copy_df])

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax = sns.boxplot(
        x="beer_name",
        y="ratings",
        data=top10_ratings_df,
        hue="Experience",
        showfliers=False,
    )
    plt.xticks(rotation=90)
    ax.set_title(f"Top 10 Beers Ratings Distribution {df_name}")
    ax.set_xlabel("Beer Name")
    ax.set_ylabel("Ratings")
