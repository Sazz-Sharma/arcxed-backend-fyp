from rest_framework import serializers
from accounts.models import User

class LeaderboardSerializer(serializers.ModelSerializer):
    total_obtained_marks = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['id', 'username', 'total_obtained_marks']
        read_only_fields = ['id', 'username', 'total_obtained_marks']

class LeaderboardUserSerializer(serializers.ModelSerializer):
    total_obtained_marks = serializers.IntegerField(read_only=True)
    rank = serializers.IntegerField(read_only=True)
    previous_daily_rank = serializers.IntegerField(read_only=True)
    previous_weekly_rank = serializers.IntegerField(read_only=True)
    rank_change = serializers.SerializerMethodField()

    def get_rank_change(self, obj):
        if not obj.previous_rank:
            return 'new'
        if obj.rank < obj.previous_rank:
            return 'up'
        elif obj.rank > obj.previous_rank:
            return 'down'
        return 'same'
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'total_obtained_marks',
            'rank',
            'previous_daily_rank',
            'previous_weekly_rank', 
            'rank_change'
        ]
