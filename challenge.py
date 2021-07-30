from elevator import Building
import random

class Action(Building):
    def __init__(self, level):
        self.n_floor    = level['n_floor'] 
        self.n_elevator = level['n_elevator'] 
        self.limit_time = level['limit_time']
        self.target_score = level['target_score']
        super().__init__(self.n_floor,self.n_elevator, self.limit_time, self.target_score)

    """
    Example : Elevators go to floor Randomly
    """
    def function(self):
        elev_action=''
        for i in range(self.n_elevator):
            if i > 0:
                elev_action += " / "
            while True:
                x = random.randint(0,self.n_floor-1)
                if self.Elevators[i].floor != x:
                    fromfloor = self.Elevators[i].floor
                    elev_action+=f"Elevator{i} : [F{fromfloor}] -> [F{x}]"
                    self.Elevators[i].goToFloor(x)
                    break
        elev_action += "\n"
        #logging.debug(f"{elev_action}")
        return elev_action

if __name__ == "__main__":
    level = {
             'n_floor':      5,
             'n_elevator':   1, 
             'limit_time':   60,
             'target_score': 30
             }
    act = Action(level)

