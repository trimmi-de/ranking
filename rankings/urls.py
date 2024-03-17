from django.urls import path

from .views import CreateMatchView, PlayerRatingListView

app_name = "rankings"
urlpatterns = [
    path('create-match/', CreateMatchView.as_view(), name='create_match'),
    path('player-ratings/', PlayerRatingListView.as_view(), name='player_ratings'),
]
