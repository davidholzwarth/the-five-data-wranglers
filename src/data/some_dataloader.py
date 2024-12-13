import pandas as pd


def load_rating_wo_text(path):
    """
    Load a ratings dataset without the text column
    :param path: the path to the ratings.csv
    :return: the loaded dataframe without the text column
    """
    return pd.read_csv(path, usecols=lambda col: col != "text")


def load_user_data(
    ba_path="src/data/BeerAdvocate/users.csv",
    rb_path="src/data/RateBeer/users.csv",
):
    """
    Loads the users.csv for both datasets
    :param ba_path: Path to the BeerAdvocate users.csv
    :param rb_path: Path to the RateBeer users.csv
    :return:
    """
    df_ba_users = pd.read_csv(ba_path)
    df_rb_users = pd.read_csv(rb_path)
    return df_ba_users, df_rb_users


def load_brewery_data(brewery_path="./data/RateBeer/breweries.csv"):
    """
    Loading the brewery dataset.
    CAUTION: The location attribute is renamed to brewery_location.
    :param brewery_path: Path to the breweries.csv
    :return: the brewery dataset in a pandas df
    """
    df_brew = pd.read_csv(brewery_path)
    df_brew.rename(
        columns={"id": "brewery_id", "location": "brewery_location"}, inplace=True
    )
    return df_brew


def load_rating_data(
    ba_path="data/BeerAdvocate/BA_ratings.csv",
    rb_path="data/RateBeer/RB_ratings.csv",
):
    """
    Loads rating data in pandas dataframes
    :return: these dataframes
    """
    df_ba_ratings = pd.read_csv(ba_path)
    df_rb_ratings = pd.read_csv(rb_path)
    return df_ba_ratings, df_rb_ratings
