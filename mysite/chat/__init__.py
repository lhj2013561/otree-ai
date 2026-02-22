from otree.api import *
from openai import OpenAI
import os


class C(BaseConstants):
    NAME_IN_URL = 'chat'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    N_TURNS = 3


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    consent = models.BooleanField(label="연구 참여에 동의합니다")

    q1 = models.IntegerField(
        label="나는 요즘 사회적으로 고립되어 있다고 느낀다",
        choices=[[1,'전혀 아니다'],[2,'2'],[3,'보통'],[4,'4'],[5,'매우 그렇다']],
        widget=widgets.RadioSelect
    )

    user_text = models.LongStringField(blank=True)

    turn = models.IntegerField(initial=1)

    trust_ai = models.IntegerField(
        label="AI의 답변을 얼마나 신뢰하시나요?",
        choices=[[1,'전혀 아님'],[2,'2'],[3,'3'],[4,'보통'],[5,'매우']],
        widget=widgets.RadioSelect
    )


class ChatLog(ExtraModel):
    player = models.Link(Player)
    turn = models.IntegerField()
    user_text = models.LongStringField()
    ai_text = models.LongStringField()


def ask_ai(text):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": text}],
        max_tokens=200
    )

    return response.choices[0].message.content


# ---------------- Pages ----------------

class Consent(Page):
    form_model = 'player'
    form_fields = ['consent']


class Survey(Page):
    form_model = 'player'
    form_fields = ['q1']


class Chat(Page):

    form_model = 'player'
    form_fields = ['user_text']

    @staticmethod
    def vars_for_template(player):
        logs = ChatLog.filter(player=player)
        logs = sorted(logs, key=lambda x: x.turn)
        return dict(logs=logs)

    @staticmethod
    def before_next_page(player, timeout_happened):

        ai = ask_ai(player.user_text)

        ChatLog.create(
            player=player,
            turn=player.turn,
            user_text=player.user_text,
            ai_text=ai,
        )

        player.turn += 1

class PostLikert(Page):
    form_model = 'player'
    form_fields = ['trust_ai']


class End(Page):
    pass


page_sequence = [
    Consent,
    Survey,
    Chat,
    Chat,
    Chat,
    PostLikert,
    End
]