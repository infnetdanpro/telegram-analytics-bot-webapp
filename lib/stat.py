import string
from collections import Counter
from typing import Dict, AnyStr, Union, List

import pymorphy2
import ujson as json


class JSONLogParserEmptyData(Exception):
    pass


class JSONLogParser:
    def __init__(self, file_name: AnyStr = None, data_dict: dict = None):
        if not any([file_name, data_dict]):
            raise JSONLogParserEmptyData('You should put data into class: file_name or data_dict')
        self.filename: AnyStr = file_name
        if self.filename:
            # parse file from disk
            self.data: Dict = JSONLogParser.parse(file_name)
        else:
            # get data from dict
            self.data = data_dict
        self.name: Union[AnyStr, None] = self.data.get("name")
        self.type: Union[AnyStr, None] = self.data.get("type")
        self.id: Union[int, None] = self.data.get("id")
        self.messages: Union[AnyStr, None] = JSONLogParser.parse_messages(
            messages=self.data.get("messages")
        )
        del self.data["messages"]
        self.unique_hashtags: set = set()
        self.hashtags: List = list()
        self.hashtags_frequency: Union[Counter, None] = None
        self.users: dict = dict()
        self.sociable_users: List[Dict] = list()
        self.messages_by_users: Dict = dict()
        self.words_stats: Dict = dict()
        self.users_replies_stats: List[Dict] = list()
        self.users_replies_data: List[Dict] = list()

    @staticmethod
    def parse(file_name: str) -> Dict:
        with open(file_name, "r", encoding="utf-8") as f:
            return json.loads(f.read())

    @staticmethod
    def parse_messages(messages: List[Dict]) -> List[Dict]:
        """Process messages only"""
        cleared_messages: List[Dict] = []
        for message in messages:
            if message.get("type") == "message":
                cleared_messages.append(message)

        return cleared_messages

    # TAGS start
    def get_hashtags(self):
        """Parsing hashtags from messages"""
        for message in self.messages:
            text = message["text"]

            if not isinstance(text, list):
                continue

            for text_item in text:
                if not isinstance(text_item, dict):
                    continue
                if not text_item.get("type") == "hashtag":
                    continue
                hashtag = text_item["text"].lower()
                self.unique_hashtags.add(hashtag)
                self.hashtags.append(hashtag)

    def sort_hashtags(self):
        temp_hashtags: list = [hashtag[1:] for hashtag in self.hashtags]
        self.hashtags = sorted(["#" + hashtag for hashtag in temp_hashtags])

    def count_hashtags(self):
        counter = Counter()
        for hashtag in self.hashtags:
            counter[hashtag] += 1

        self.hashtags_frequency: dict = counter

    def tags_stats(self):
        # TODO: do it in threads?
        self.get_hashtags()
        self.sort_hashtags()
        self.count_hashtags()

        return {
            "unique_hashtags": self.unique_hashtags,
            "hashtags_frequency": self.hashtags_frequency,
        }

    # TAGS end

    # USERS start
    def get_users(self):
        for message in self.messages:
            self.users[message["from_id"]] = message["from"]

    def get_most_sociable_user(self):
        counter = Counter()
        for message in self.messages:
            counter[message["from_id"]] += 1

        sociable_users = []
        for from_id, amount in dict(counter).items():
            sociable_users.append(
                {
                    "from_id": from_id,
                    "name": self.users[from_id],
                    "amount": amount,
                }
            )
        self.sociable_users = sorted(sociable_users, key=lambda x: -x["amount"])

    def get_user_messages(self):
        """For get messages by user"""
        user_messages = {}
        for message in self.messages:
            from_id = message["from_id"]
            text = message["text"]
            date = message["date"]

            if isinstance(text, list):
                temp_text = []
                for text_elem in text:
                    if isinstance(text_elem, str):
                        temp_text.append(text_elem)
                    elif isinstance(text_elem, dict):
                        temp_text.append(text_elem["text"])

                text = " ".join(temp_text)

            message_obj = {"date": date, "text": text}
            if user_messages.get(from_id):
                user_messages[from_id].append(message_obj)
            else:
                user_messages[from_id] = [message_obj]

        self.messages_by_users = user_messages

    def get_user_stats(self):
        # TODO: do it in threads?
        self.get_users()
        self.get_most_sociable_user()
        self.get_user_messages()

        return {
            "users": self.users,
            "messages": self.messages_by_users,
        }

    # USERS end

    # TODO:
    # top 10-15-20-25-30 of most common words
    # WORDS Stats start
    def get_all_words(self) -> list:
        def clear_text(sentence: str) -> str:
            result_sentence = []
            words = sentence.split(" ")
            en_rus_strings = (
                string.ascii_letters + "йцукенгшщзхъфывапролджэячсмитьбюё €-1234567890"
            )

            for word in words:
                if word.startswith("http"):
                    result_sentence.append(word)
                else:
                    temp_word = ""
                    for letter in word:
                        if letter in en_rus_strings:
                            temp_word += letter
                    result_sentence.append(temp_word)

            return " ".join(result_sentence)

        messages = []
        for message in self.messages:
            original_text = message["text"]

            if isinstance(original_text, list):
                temp_text = []
                for text_elem in original_text:
                    if isinstance(text_elem, str):
                        temp_text.append(text_elem.lower())
                    elif isinstance(text_elem, dict):
                        temp_text.append(text_elem["text"])
                original_text = " ".join(temp_text)
            else:
                original_text = original_text.lower()
            text = clear_text(original_text)
            text = [t for t in text.split(" ") if t]
            if text:
                messages.extend(text)
        return messages

    def get_words_stats(self, words: List[str]):
        counter = Counter()
        morph = pymorphy2.MorphAnalyzer()
        for word in words:
            # TODO: threads here?>
            counter[morph.parse(word)[0].normal_form] += 1

        self.words_stats = counter

    # most replied user
    def get_most_replied_user(self):
        replied_messages = {}
        for message in self.messages:
            if message.get("reply_to_message_id"):
                if replied_messages.get(message["reply_to_message_id"]):
                    replied_messages[message["reply_to_message_id"]].append(message)
                else:
                    replied_messages[message["reply_to_message_id"]] = [message]

        users = {}
        # We need get authors of each message_id:
        authors_replied_messages = {}
        for message in self.messages:
            if replied_messages.get(message["id"]):
                users[message["from_id"]] = message["from"]
                authors_replied_messages[message["from_id"]] = replied_messages[
                    message["id"]
                ]

        authors_items = []
        for from_id, values in authors_replied_messages.items():
            authors_items.append(
                {"from_id": from_id, "count": len(values), "from": users[from_id]}
            )
        authors_items = sorted(authors_items, key=lambda x: -x["count"])
        self.users_replies_stats: List[Dict] = authors_items
        self.users_replies_data: List[Dict] = authors_replied_messages


if __name__ == "__main__":
    filename = "result.json"
    data = JSONLogParser(file_name=filename)
    data.get_most_replied_user()

    print(data.users_replies_stats)
