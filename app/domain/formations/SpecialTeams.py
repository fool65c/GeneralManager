from app.domain.formations.Formation import Formation


class SpecialTeams(Formation):
    def __init__(self):
        self.positions = {
            'K': 1,
            'P': 1
        }

        super().__init__(self.positions)
