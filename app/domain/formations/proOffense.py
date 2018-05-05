from app.domain.formations.Formation import Formation


class proOffense(Formation):
    def __init__(self):
        self.positions = {
            'QB': 1,
            'RB': 2,
            "WR": 2,
            "TE": 1,
            "OL": 5
        }

        super().__init__(self.positions)
