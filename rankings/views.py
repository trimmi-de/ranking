from django.db.models import Count, Q
from django.views.generic import ListView

from rankings.models import PlayerRating, Club
from .forms import CreateMatchForm


class PlayerRatingListView(ListView):
    model = PlayerRating
    template_name = 'player_rating_list.html'
    context_object_name = 'player_ratings'

    def get_queryset(self):
        # Group players by club and annotate each group with player count
        queryset = Club.objects.annotate(num_players=Count('player'))

        # Retrieve player ratings for each club within a given date range
        current_date = datetime.now().date()
        for club in queryset:
            club.player_ratings = PlayerRating.objects.filter(
                Q(player__club=club) & (
                    Q(start_date__lte=current_date, end_date__gte=current_date) |
                    Q(end_date__isnull=True)
                )
            )

        return queryset


from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .models import Match, MatchPlayer, PlayerRating
import trueskill
from datetime import datetime


class CreateMatchView(FormView):
    template_name = 'create_match.html'
    form_class = CreateMatchForm  # Replace YourMatchForm with your actual form class
    success_url = reverse_lazy('match_list')

    def form_valid(self, form):
        # Assuming form data is submitted with player IDs and a winner
        player_ids = form.cleaned_data.get('players')
        winner_id = form.cleaned_data.get('winner')

        # Create the match
        match = Match.objects.create()

        # Add players to the match
        for i, player_id in enumerate(player_ids):
            match_player = MatchPlayer.objects.create(player_id=player_id, match=match, team_number=i + 1)

        # Set the winner of the match
        match.winner_id = winner_id
        match.save()

        # Calculate and update Trueskill ratings
        self.calculate_trueskill_ratings(match, datetime.now().date())

        return super().form_valid(form)

    def calculate_trueskill_ratings(self, match, current_date):
        # Retrieve all players involved in the match
        players = match.players.all()
        team_ratings = []

        # Get Trueskill ratings for each player
        for player in players:
            rating = trueskill.Rating(mu=player.trueskill_mu, sigma=player.trueskill_sigma)
            team_ratings.append(rating)

        # Get the ranks of the teams based on the winner of the match
        ranks = [1 if player == match.winner else 0 for player in players]

        # Calculate the new ratings based on the match outcome
        new_ratings = trueskill.rate([team_ratings], ranks=ranks)[0]

        # Update the ratings in the database
        for i, player in enumerate(players):
            # Close the existing rating record if it's still open
            open_rating = PlayerRating.objects.filter(player=player, end_date__isnull=True).first()
            if open_rating:
                open_rating.end_date = current_date
                open_rating.save()

            # Create a new rating record with the current ratings
            player_rating = PlayerRating.objects.create(
                player=player,
                trueskill_mu=new_ratings[i].mu,
                trueskill_sigma=new_ratings[i].sigma,
                start_date=current_date
            )
