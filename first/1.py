class Action:
    def update(self, State):
        pass

class AddItem(Action):
    def __init__(self, **argv):
        self.argv = argv

    def update(self, State):
        State['end'] = 1
        for k, v in self.argv.iteritems():
            State[k] = v

class AddItemWithCount(Action):
    def __init__(self, **argv):
        self.argv = argv

    def update(self, State):
        State['end'] = 1
        for k, v in self.argv.iteritems():
            State[k] = v


class GotoQuestion(Action):
    def __init__(self, next_, **argv):
        self.next_ = next_
        self.argv = argv

    def update(self, State):
        State['CurrentQuestion'] = self.next_
        for k, v in self.argv.iteritems():
            State[k] = v

class DefaultAction(Action):
    def update(self, State):
        pass

class Answer:
    def __init__(self):
        pass

class Question:
    def __init__(self, Q, Answers, Any=DefaultAction()):
        self.Q = Q
        self.Answers = Answers
        self.Any = Any

    def Ask(self, State):
        return self.Q, self.Answers.keys()

    def WhatNext(self, answer, State):
        if answer in self.Answers:
            return self.Answers[answer]
        else:
            digit = -1
            try:
                digit = int(answer)
            except:
                pass
            if digit == -1:
                return self.Any
            if digit <= len(self.Answers) and digit > 0:
                return self.Answers[self.Answers.keys()[digit - 1]]
            else:
                return self.Any

class QuesitonSelectFew:
    def __init__(self, Q, Answers, FuncAction, Any=DefaultAction(), saveTo='item'):
        self.Q = Q
        self.Answers = Answers
        self.Any = Any
        self.FuncAction = FuncAction
        self.saveTo='item'

    def getItems(self, State):
        result = []
        for answer, values in self.Answers.iteritems():
            if all([State[k] == v for k,v in values.iteritems()]):
                result.append(answer)
        return result

    def Ask(self, State):
        return self.Q, self.getItems(State)

    def WhatNext(self, answer, State):
        items = self.getItems(State)
        if answer in items:
            State[self.saveTo] = answer
            return self.FuncAction
        else:
            digit = -1
            try:
                digit = int(answer)
            except:
                pass
            if digit == -1:
                return self.Any
            if digit <= len(items) and digit > 0:
                State[self.saveTo] = items[digit - 1]
                return self.FuncAction
            else:
                return self.Any


class QuestionCount(Question):
    def __init__(self, Q, Any=DefaultAction()):
        self.Q = Q
        self.Any = Any

    def Ask(self, State):
        return self.Q, []

    def WhatNext(self, answer, State):
        digit = -1
        try:
            digit = int(answer)
        except:
            pass
        if digit:
            return AddItemWithCount(count=digit)
        else:
            return self.Any

class State:
    def __init__(self):
        pass

class TItem:
    def __init__(self, Name, Questions, FirstQuestion):
        self.FirstQuestion = FirstQuestion
        self.Questions = Questions
        self.Name = Name

    def doFirst(self):
        State = {}
        State['CurrentQuestion'] = self.FirstQuestion
        q, items = self.Questions[State['CurrentQuestion']].Ask(State)
        return q, items, State

    def do(self, answer, State):
        action = self.Questions[State['CurrentQuestion']].WhatNext(answer, State)
        action.update(State)
        if 'end' in State and State['end']:
            return None, (State['item'], State.get('count', 1)), None
        q, items = self.Questions[State['CurrentQuestion']].Ask(State)
        return q, items, State


def CD(**argv):
    return argv
def Create(b, c):
    return {'bankatype': b, 'color': c}


Beer = TItem("Beer", {'Usual':
                 Question("Как обычно?", {"Да": AddItem(item="Жигули 4.9% 0.5 литра"), "Нет": GotoQuestion("BeerType")}),
             'BeerType':
                 Question("Какое хотите?", {"Жигули": GotoQuestion("HowMany", item="Жигули 4.9% 0.5 литра"),
                                            "Балтика№0": GotoQuestion("HowMany", item="Балтика 0.5% 0.5 литра"),
                                            "Балтика№3": GotoQuestion("HowMany", item="Балтика 4.8% 0.5 литра"),

                                            "Другое": GotoQuestion("Other")}),
             'HowMany':
                 QuestionCount("Сколько?"),
             'Other':
                 Question("Темное или светлое?", {"Темное": GotoQuestion("BankaType", color="black"),
                                                  "Светлое": GotoQuestion("BankaType", color="white")}),
             'BankaType':
                  Question("Банка или бутылка?", {"Банка": GotoQuestion("SelectFew", bankatype="banka"),
                                                   "Бутылка": GotoQuestion("SelectFew", bankatype="butilka")}),
             'SelectFew':
                  QuesitonSelectFew("Сделайте выбор!", {'Жигули 3% black': Create("banka", "black"),
                                                        'Жигули 3% white': Create("banka", "white"),
                                                        'Жигули 3% butilka black': Create("butilka", "black"),
                                                        'Жигули 3% butilka white': Create("butilka", "white"),
                                                        'Жигули 9% black': Create("banka", "black"),
                                                        'Жигули 9% white': Create("banka", "white"),
                                                        'Жигули 9% butilka black': Create("butilka", "black"),
                                                        'Жигули 9% butilka white': Create("butilka", "white")},
                                    GotoQuestion("HowMany"), saveTo='item')
            }, "Usual")

def Print(All):
    if All[0]:
        print All[0]
        for i, x in enumerate(All[1]):
            print i + 1, x
    else:
        print "Добавили товар", All[1][0], "в количестве", All[1][1]
