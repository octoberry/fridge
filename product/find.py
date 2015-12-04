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

    def __init__(self, Q, Targets, Answers, FuncAction, Any=None, saveTo='item'):
        self.Q = Q
        self.Answers = Answers
        self.Any = Any or DefaultAction()
        self.FuncAction = FuncAction
        self.Targets = Targets
        self.saveTo = saveTo

    def getItems(self, State):
        result = []
        for answer, values in self.Answers.iteritems():
            if all([State[k] == values[k] for k in self.Targets['select']]):
                result.append(answer)
        result = sorted(result, key=lambda x: abs(self.Answers[x][self.Targets['sort']] - State['price']))
        result = map(lambda x: x + u', цена: ' + str(self.Answers[x]['price']), result)
        return result

    def Ask(self, State):
        return self.Q, self.getItems(State)

    def TryMatchPrice(self, real_answer):
        for answer, values in self.Answers.iteritems():
            if 'price' in values and real_answer.startswith(answer):
                return values['price']
        return None

    def WhatNext(self, answer, State):
        items = self.getItems(State)
        if answer in items:
            State[self.saveTo] = answer
            price = self.TryMatchPrice(answer)
            if price is not None:
                State['price'] = price
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

    def __init__(self, Q, field, func, Any=None):
        self.Q = Q
        self.field = field
        self.func = func
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
            return self.func({self.field: digit})
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
            return None, (State['item'], State.get('count', 1), State['price']), None
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
                #  save item to cart
                del State['Current']
                return Z[0], Z[1], State
        else:
            if 'words' not in State or not State['words']:
                State['words'] = re.findall(ur'(?u)\w+', query)
        q, items = self.doNextWord(State)
        return q, items, State


def ExtendDict(**argv):
    return argv


def CreateBeer(b, c, p):
    return {'bankatype': b, 'color': c, 'price': p}


def CreateMilk(fast, fat, price):
    return {'fast': fast, 'fat': fat, 'price': price}


Beer = TItem(u"Пиво",
             {'Usual': Question(u"Как обычно?",
                                {u"Да": AddItem(item=u"Жигули 4.9% 0.5 литра", price='40'),
                                 u"Нет": GotoQuestion("BeerType")}),
              'BeerType': Question(u"Какое хотите?", {
                  u"Жигули": GotoQuestion("HowMany", item="Жигули 4.9% 0.5 литра", price=40),
                  u"Балтика№0": GotoQuestion("HowMany", item=u"Балтика 0.5% 0.5 литра", price=50),
                  u"Балтика№3": GotoQuestion("HowMany", item=u"Балтика 4.8% 0.5 литра", price=80),
                  u"Другое": GotoQuestion("Other")}),
              'HowMany': QuestionCount(u"Сколько?", 'count',
                  lambda x: AddItemWithCount(**x)),
              'ApproxPrice': QuestionCount(u"Приблизительная цена?", 'price', lambda x:
                  GotoQuestion('SelectFew', **x)),
              'Other': Question(u"Темное или светлое?",
                                {u"Темное": GotoQuestion("BankaType", color="black"),
                                 u"Светлое": GotoQuestion("BankaType", color="white")}),
              'BankaType': Question("Банка или бутылка?",
                                    {u"Банка": GotoQuestion("ApproxPrice", bankatype="banka"),
                                     u"Бутылка": GotoQuestion("ApproxPrice", bankatype="butilka")}),
                                    'SelectFew': QuesitonSelectFew(u"Сделайте выбор!", {'select':
                                        ['color', 'bankatype'], 'sort': 'price'}, {
                    u'Жигули 3% black': CreateBeer("banka", "black", 30),
                    u'Жигули 3% white': CreateBeer("banka", "white", 50),
                    u'Жигули 3% butilka black': CreateBeer("butilka", "black", 80),
                    u'Жигули 3% butilka white': CreateBeer("butilka", "white", 90),
                    u'Жигули 9% black': CreateBeer("banka", "black", 102),
                    u'Жигули 9% white': CreateBeer("banka", "white", 30),
                    u'Жигули 9% butilka black': CreateBeer("butilka", "black", 50),
                    u'Жигули 9% butilka white': CreateBeer("butilka", "white", 20)},
                                             GotoQuestion("HowMany"), saveTo='item')}, "BeerType")

Sosige = TItem(u"Сосиски",
             {'Usual': Question(u"Как обычно?",
                                {u"Да": AddItem(item=u"Сосиски Клинские 300 грамм", price='130'),
                                 u"Нет": AddItem(item=u"Сосиски НеКлинские не любимые 300 грамм", price='70')})}, 'Usual')

Naggets = TItem(u"Наггетсы",
             {'Usual': Question(u"Как обычно?",
                                {u"Да": AddItem(item=u"Наггетсы c сыром Клинские 300 грамм", price='130'),
                                 u"Нет": AddItem(item=u"Наггетсы НеКлинские не любимые 300 грамм", price='70')})}, 'Usual')

Milk = TItem(u"Молоко",
             {'Usual': Question(u"Как обычно?",
                                {u"Да": AddItem(item=u"Молоко 1 литр пастеризованное", price='60'),
                                 u"Нет": GotoQuestion("MilkType")} ),
              'HowMany': QuestionCount(u"Сколько?", 'count',
                  lambda x: AddItemWithCount(**x)),
              'MilkType': Question('Какое хотите?', {
                  u'Ясный луч 3.2% 1л, ультрапастеризованное': GotoQuestion("HowMany", item=u'Ясный луч 3.2% 1л, ультрапастеризованное', price=80),
                  u'Простоквашно 3,4-4,5% пастеризованое': GotoQuestion("HowMany",
                      item=u'Простоквашно 3,4-4,5% пастеризованое', price=75),
                  u'Домик в деревне ультрапастеризованное, 3.2%': GotoQuestion("HowMany",
                      item=u'Простоквашно 3,4-4,5% пастеризованое', price=75),
                  u'Другое':GotoQuestion("Other")}),
              'Other': Question(u"Скоропортящееся?",
                                {u"Да": GotoQuestion("fat", fast='1'),
                                 u"Нет": GotoQuestion("fat", fast='2')}),
              'ApproxPrice': QuestionCount(u"Приблизительная цена?", 'price', lambda x:
                  GotoQuestion('select', **x)),
              'fat': Question(u'Жирность?', {
                                  u'Диетическое': GotoQuestion("ApproxPrice", fat='0'),
                                  u'Средней жирности': GotoQuestion("ApproxPrice", fat='1'),
                                  u'Жирное': GotoQuestion("ApproxPrice", fat='2')}),
              'select':  QuesitonSelectFew(u"Время делать выбор!", {'select': ['fat', 'fast'],
                  'sort': 'price'}, {
                    u'Ясный луч 3.2% 1л, ультрапастеризованное': CreateMilk("1", "0", 60),
                    u'Простоквашно 3,4-4,5% пастеризованое': CreateMilk("1", "1", 60),
                    u'Самое лучше молоко': CreateMilk("1", "2", 60),
                    u'Самое худшее молоко': CreateMilk("2", "0", 60),
                    u'Домик в деревне ультрапастеризованное, 3.2%': CreateMilk("2", "1", 60),
                    u'Неизвестная марка молока': CreateMilk("2", "2", 60),
                      }, GotoQuestion("HowMany"), saveTo='item')
              }, 'Usual')


def Print(All):
    if All[0]:
        print All[0]
        for i, x in enumerate(All[1]):
            print i + 1, x
    else:
        print u"Добавили товар", All[1][0], u"в количестве", All[1][1]


Items = TItems([Beer, Sosige, Naggets, Milk])
