from core.models import Achievement

def award_badge(user, badge_name):
    """
    Awards a badge to the user if not already earned.
    """
    if not Achievement.objects.filter(user=user, badge_name=badge_name).exists():
        Achievement.objects.create(user=user, badge_name=badge_name)
