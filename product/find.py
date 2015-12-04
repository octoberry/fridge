# coding=utf-8
import re


class Action(object):

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


class Answer(object):

    def __init__(self):
        pass


class Question(object):

    def __init__(self, Q, Answers, Any=None):
        self.Q = Q
        self.Answers = Answers
        self.Any = Any or DefaultAction()

    def Ask(self, State):
        return self.Q, self.Answers.keys()

    def WhatNext(self, answer, State):
        if answer.lower() in set(map(lambda x: x.lower(), self.Answers.keys())):
            return self.Answers[answer]
        else:
            digit = -1
            try:
                digit = int(answer)
            except Exception:
                pass
            if digit == -1:
                return self.Any
            if digit <= len(self.Answers) and digit > 0:
                return self.Answers[self.Answers.keys()[digit - 1]]
            else:
                return self.Any


class QuesitonSelectFew(object):

    def __init__(self, Q, Answers, FuncAction, Any=None, saveTo='item'):
        self.Q = Q
        self.Answers = Answers
        self.Any = Any or DefaultAction()
        self.FuncAction = FuncAction
        self.saveTo = saveTo

    def getItems(self, State):
        result = []
        for answer, values in self.Answers.iteritems():
            if all([State[k] == v for k, v in values.iteritems()]):
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
            except Exception:
                pass
            if digit == -1:
                return self.Any
            if digit <= len(items) and digit > 0:
                State[self.saveTo] = items[digit - 1]
                return self.FuncAction
            else:
                return self.Any


class QuestionCount(Question):

    def __init__(self, Q, Any=None):
        self.Q = Q
        self.Any = Any or DefaultAction()

    def Ask(self, State):
        return self.Q, []

    def WhatNext(self, answer, State):
        digit = -1
        try:
            digit = int(answer)
        except Exception:
            pass
        if digit:
            return AddItemWithCount(count=digit)
        else:
            return self.Any


class State(object):

    def __init__(self):
        pass


class TItem(object):

    def __init__(self, Name, Questions, FirstQuestion):
        self.FirstQuestion = FirstQuestion
        self.Questions = Questions
        self.Name = Name

    def doFirst(self):
        State = {'CurrentQuestion': self.FirstQuestion}
        q, items = self.Questions[State['CurrentQuestion']].Ask(State)
        return q, items, State

    def do(self, answer, State):
        action = self.Questions[State['CurrentQuestion']].WhatNext(answer, State)
        action.update(State)
        if 'end' in State and State['end']:
            return None, (State['item'], State.get('count', 1)), None
        q, items = self.Questions[State['CurrentQuestion']].Ask(State)
        return q, items, State


class TItems(object):

    def __init__(self, items):
        self.items = dict(map(lambda x: (x.Name.lower(), x), items))

    def doNextWord(self, State):
        words = State['words']
        if not words:
            return "Заказываем?", []
        word = words[0]
        words = words[1:]
        State['words'] = words
        if word in self.items:
            q, items, State['State'] = self.items[word].doFirst()
            State['Current'] = word
        else:
            q = u"Я не знаю такого товара"
            items = []
        return q, items

    def do(self, query, State):
        if 'Current' in State:
            Z = self.items[State['Current']].do(query, State['State'])
            State['State'] = Z[2]
            if Z[0] is not None:
                return Z[0], Z[1], State
            else:
                del State['Current']
        else:
            State['words'] = re.findall(ur'(?u)\w+', query)
            print State['words']
        q, items = self.doNextWord(State)
        return q, items, State


def CD(**argv):
    return argv


def Create(b, c, p):
    return {'bankatype': b, 'color': c, 'price': p}


Beer = TItem(u"Пиво",
             {'Usual': Question(u"Как обычно?",
                                {u"Да": AddItem(item=u"Жигули 4.9% 0.5 литра"),
                                 u"Нет": GotoQuestion("BeerType")}),
              'BeerType': Question(u"Какое хотите?", {
                  u"Жигули": GotoQuestion("HowMany", item="Жигули 4.9% 0.5 литра"),
                  u"Балтика№0": GotoQuestion("HowMany", item=u"Балтика 0.5% 0.5 литра"),
                  u"Балтика№3": GotoQuestion("HowMany", item=u"Балтика 4.8% 0.5 литра"),
                  u"Другое": GotoQuestion("Other")}),
              'HowMany': QuestionCount(u"Сколько?"),
              'Other': Question(u"Темное или светлое?",
                                {u"Темное": GotoQuestion("BankaType", color="black"),
                                 u"Светлое": GotoQuestion("BankaType", color="white")}),
              'BankaType': Question("Банка или бутылка?",
                                    {u"Банка": GotoQuestion("SelectFew", bankatype="banka"),
                                     u"Бутылка": GotoQuestion("SelectFew", bankatype="butilka")}),
              'SelectFew': QuesitonSelectFew(u"Сделайте выбор!", {
                    u'Жигули 3% black': Create("banka", "black", 30),
                    u'Жигули 3% white': Create("banka", "white", 50),
                    u'Жигули 3% butilka black': Create("butilka", "black", 80),
                    u'Жигули 3% butilka white': Create("butilka", "white", 90),
                    u'Жигули 9% black': Create("banka", "black", 102),
                    u'Жигули 9% white': Create("banka", "white", 30),
                    u'Жигули 9% butilka black': Create("butilka", "black", 50),
                    u'Жигули 9% butilka white': Create("butilka", "white", 20)},
                                             GotoQuestion("HowMany"), saveTo='item')}, "Usual")


def Print(All):
    if All[0]:
        print All[0]
        for i, x in enumerate(All[1]):
            print i + 1, x
    else:
        print u"Добавили товар", All[1][0], u"в количестве", All[1][1]


Items = TItems([Beer])