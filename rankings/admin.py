from django.contrib import admin

from rankings.models import Club, Player, PlayerRating, Match, MatchPlayer

admin.site.register(Club)
admin.site.register(Player)
admin.site.register(PlayerRating)
admin.site.register(Match)
admin.site.register(MatchPlayer)
