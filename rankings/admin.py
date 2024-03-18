from django.contrib import admin

from rankings.models import Club, Player, PlayerRating, Match, Team


class MatchAdmin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        # Clear the many-to-many relationship with teams for each match in the queryset
        for match in queryset:
            match.teams.clear()
        # Call the delete() method to delete the queryset of Match instances
        queryset.delete()

    def delete_model(self, request, obj):
        # Clear the many-to-many relationship with teams
        obj.teams.clear()
        # Call the delete() method to delete the Match instance
        obj.delete()


admin.site.register(Match, MatchAdmin)

admin.site.register(Club)
admin.site.register(Player)
admin.site.register(PlayerRating)
admin.site.register(Team)
