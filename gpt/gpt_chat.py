import json

from openai import error

from gpt.gpt import Gpt


class ChatGpt(Gpt):
    def __init__(self, model: str = "gpt-3.5-turbo"):
        super().__init__()
        self.model = model
        self.msg_history = []

    def start_chat(self, exit_word='q'):
        """
        Chat with GPT
        :param exit_word: a word to end the chat
        :return:
        """
        while True:
            question = input("Enter your question: ")
            if question == exit_word:
                break

            answer = self.get_answer(question)
            print(answer)

    def get_competition(self, message):
        """
        Get response competition
        :param message:
        :return:
        """
        # Save previous message
        # TODO maybe need to add length limit to self.msg_history
        self.msg_history.append(message)
        try:
            completion = self.op.ChatCompletion.create(
                model=self.model,
                messages=self.msg_history
            )

            data_comp = json.loads(str(completion))
            return data_comp
        except error.RateLimitError as err:
            print('RateLimitError: ', err)

    def get_answer(self, question: str, role='user'):
        """
        Ask a question and get an answer
        :param question:
        :param role: may be:
        'user'
        'system'
        'assistant'
        :return: answer on question
        """
        msg = gpt_message(question, role)

        comp = self.get_competition(msg)
        if not is_competition_complete(comp):
            pass
        return parse_answer(comp)

    def clear_history(self):
        self.msg_history.clear()


def gpt_message(content: str, role='user'):
    """
    Convert text to gpt message entity
    :param content:
    :param role:
    :return:
    """
    return {"role": role,
            "content": content}


def parse_answer(competition):
    """
    Parse answer message from gpt competition
    :param competition: answer competition
    :type openai.openai_object.OpenAIObject
    :return:
    """
    return competition['choices'][0]['message']['content'].strip()


def is_competition_complete(competition):
    """
    Check is competition completed
    :param competition:
    :return:
    """
    finish_reason = competition['choices'][0]['finish_reason']
    if finish_reason != 'stop':
        print(f"Competition do not complete: {finish_reason}")
        return False
    return True
