from app.domain.formations.Formation import Formation


class Defense44(Formation):
    def __init__(self):
        self.positions = {
            'DL': 4,
            'LB': 4,
            'DB': 3
        }

        super().__init__(self.positions)
