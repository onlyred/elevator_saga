import random
import time
import sys
import re
import logging

WAITING=0
IN_ELEVATOR=1
DONE=2
PEOPLE_CHARACTER="\U0001F464"

logging.basicConfig(filename='log.txt', level=logging.DEBUG)

class Reprinter:
    def __init__(self):
        self.text = ''

    def moveup(self, lines):
        for _ in range(lines):
            sys.stdout.write("\x1b[A")

    def reprint(self, text):
        # Clear previous text by overwritig non-spaces with spaces
        self.moveup(self.text.count("\n"))
        sys.stdout.write(re.sub(r"[^\s]", " ", self.text))

        # Print new text
        lines = min(self.text.count("\n"), text.count("\n"))
        self.moveup(lines)
        sys.stdout.write(text)
        self.text = text

class Person:
    def __init__(self, fromfloor, tofloor):
        self.__status = WAITING
        self.__fromfloor = fromfloor
        self.__tofloor = tofloor

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, stat):
        self.__status = stat

    @property
    def fromfloor(self):
        return self.__fromfloor

    @property
    def tofloor(self):
        return self.__tofloor

class Elevator:
    def __init__(self, floor, max_boarding=4):
        self.floor = floor
        self.isfull  = False
        self.max_boarding = max_boarding
        self.__n_person = 0

    @property
    def n_person(self):
        return self.__n_person

    def goToFloor(self, tofloor):
        self.floor = tofloor

    def unboarding(self, person):
        if person.status == IN_ELEVATOR and person.tofloor == self.floor:
            self.__n_person -= 1
            self.isfull = False
            return True
        else:
            return False

    def boarding(self, person):
        if self.__n_person == self.max_boarding:
            self.isfull= True
        else:
            self.isfull= False
            if person.status == WAITING and person.fromfloor == self.floor:
                self.__n_person += 1
                return True
        return False


    def isFull(self):
        if self.isfull:
            return True
        else:
            return False

class Building:
    def __init__(self, n_floor, n_elevator, limit_time, target_score):
        '''
           n_floor    : number of floor in Building
           n_elevator : number of elevator in Building
           limit_time : Time Limit (Seconds)
           target_score: number of peole arriving at the destination
        '''
        self.max_waiting = 5
        self.Elevators= []
        self.Persons = []
        self.n_elevator = n_elevator
        self.n_floor = n_floor
        self.n_person = [0]*self.n_floor
        self.target_score = target_score
        self.limit_time     = limit_time
        self.score  = 0
        self.start_time   = time.time()
        self.func   = []
        self.reprinter = Reprinter()

        for i in range(n_elevator):
            self.Elevators.append(Elevator(random.randint(0,self.n_floor-1)))

        self.run()

    def _draw_person(self, floor_num, padding=''):
        n_person = 0
        person_character = padding + ''
        for person in self.Persons:
            if n_person == self.max_waiting:
                break
            if person.fromfloor == floor_num and person.status == WAITING:
                person_character += PEOPLE_CHARACTER
                n_person += 1
        person_character += '  ' * (self.max_waiting - n_person)
        return person_character + padding

    def _draw_elevator(self, elev, padding=''):
        elev_character   = padding + '['
        for i in range(elev.max_boarding):
            if i < elev.n_person:
                elev_character += PEOPLE_CHARACTER
            else:
                elev_character += '  '
        elev_character += ']' 
        return elev_character + padding

    def gen_waiting_person(self, maxnum):
        n_gen = random.randint(1,maxnum)
        for i in range(n_gen):
            while True:
                person = Person(random.randint(0,self.n_floor-1), random.randint(0,self.n_floor-1))
                if person.fromfloor != person.tofloor:
                    break
            self.Persons.append(person)

    def draw(self, action='\n'):
        tempfile= open('log.txt','a')
        title = (f"Challenge # Transport {self.target_score} people in {self.limit_time} seconds or less\n")
        score_board = (f"Score : {self.score}\n")
        padding = '  '
        character = title + score_board + action
        for floor_number in range(self.n_floor-1, -1, -1): 
            n_person_floor = 0
            for person in self.Persons:
                if person.status == WAITING and person.fromfloor == floor_number:
                    n_person_floor += 1
            character += f"[{floor_number} F] ({n_person_floor}) "
            character += self._draw_person(floor_number)
            for elev in self.Elevators:
                if elev.floor == floor_number:
                    character += self._draw_elevator(elev, padding)
                else:
                    character += padding + ' ' + '  '*elev.max_boarding + ' ' + padding
            for i, person in enumerate(self.Persons):
                if person.status == DONE and person.tofloor == floor_number:
                    character += PEOPLE_CHARACTER
            character += " "*10 + "\n"
        self.reprinter.reprint(character)
        time.sleep(1)
        tempfile.close()

    def _removeDone(self):
        length = len(self.Persons)
        for i in range(length-1, -1, -1):
            if self.Persons[i].status == DONE:
                del self.Persons[i]

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

    def _logging(self, title):
        logging.debug(f"> {title}")
        logging.debug(f"nPerson : {len(self.Persons)}")
        for i, p in enumerate(self.Persons):
            logging.debug(f"Status : {p.status}, fromfloor : {p.fromfloor}, tofloor : {p.tofloor}")

    def run(self):
        self.gen_waiting_person(self.max_waiting)
        self.draw("Start\n")
        while True:
            n_boarding=0
            n_unboarding=0
            # Boarding
            for elev in self.Elevators:
                for i in range(len(self.Persons)):
                    if elev.boarding(self.Persons[i]):
                        n_boarding+=1
                        self.Persons[i].status = IN_ELEVATOR
                    if elev.isFull():
                        break
            #self._logging('after boarding')    
            self.draw(f'Boarding : {n_boarding}\n')
            elev_action = self.function() # action
            self.draw(elev_action)
            # Unboarding
            for elev in self.Elevators:
                for i in range(len(self.Persons)):
                    if elev.unboarding(self.Persons[i]):
                        n_unboarding+=1
                        self.Persons[i].status = DONE
                        self.score += 1
            #self._logging('after unboarding')    
            self.draw(f'Unboading : {n_unboarding}\n')
            self._removeDone()
            #self._logging('after remove')    
            if self.target_score == self.score: 
                print("Success!")
                break
            elif time.time() - self.start_time > self.limit_time:
                print("Fail...")
                break
            self.gen_waiting_person(self.max_waiting)
            self.draw(f'Generate Persons\n')

#if __name__ == "__main__":
#    #random.seed(1)
#    Building(n_floor=5, n_elevator=1, limit_time=60, target_score=10)

