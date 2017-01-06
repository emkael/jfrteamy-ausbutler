def cutoff(score, cutoff_point=32, cutoff_rate=0.1):
    sign = 1 if score > 0 else -1
    score = abs(score)
    if score > cutoff_point:
        score -= cutoff_point
        score *= cutoff_rate
        score += cutoff_point
    return score * sign


def get_opponents(butler, player):
    table = butler.table
    if player in [table.openE, table.openW]:
        return [table.openN, table.openS]
    if player in [table.openN, table.openS]:
        return [table.openE, table.openW]
    if player in [table.closeE, table.closeW]:
        return [table.closeN, table.closeS]
    if player in [table.closeN, table.closeS]:
        return [table.closeE, table.closeW]


def get_room(butler, player):
    table = butler.table
    if player in [table.openE, table.openW, table.openN, table.openS]:
        return 'open'
    if player in [table.closeE, table.closeW, table.closeN, table.closeS]:
        return 'closed'


def get_line(butler, player):
    table = butler.table
    room = get_room(butler, player).upper()
    direction = 'NS' if player in [
        table.openN, table.openS, table.closeN, table.closeS
    ] else 'EW'
    return '%s_%s' % (room, direction)


def normalize(butler, opp_factor=0.5):
    if butler.board_count == 0:
        return 0.0
    return (
        butler.cut_score / butler.board_count +
        butler.opp_score * opp_factor
    ) * butler.board_count
