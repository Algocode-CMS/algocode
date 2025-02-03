from courses.models import ParticipantsGroup


def get_participants_group(participant_group: ParticipantsGroup) -> dict:
    group = {
        'name': participant_group.name,
        'short_name': participant_group.short_name,
        'participants': []
    }
    for participant in participant_group.participants.all():
        group['participants'].append({
            'id': participant.id,
            'name': participant.name
        })
    return group
