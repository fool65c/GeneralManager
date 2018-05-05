class Formation:
    def __init__(self, positions):
        self.positions = positions
        self.positionRanking = {}
        self.rating = 0

    def setStarters(self, roster):
        for position, count in self.positions.items():
            currentStarters = 0
            self.positionRanking[position] = 0
            for player in roster.getPositionBySkill(position):
                if currentStarters < count:
                    player.starter = True
                    self.positionRanking[position] += player.player\
                                                            .getOverallLevel()
                    currentStarters += 1
                else:
                    player.starter = False
            self.rating += self.positionRanking[position] / count
