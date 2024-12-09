from src.data.some_dataloader import *
from src.models.seasonality_analysis import *

df_ba_ratings, df_rb_ratings = load_rating_data()
STYLES_BA = df_ba_ratings['style'].unique()

