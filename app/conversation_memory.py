class ConversationMemory:
    """
    Stores the conversation for the current session.
    """

    def __init__(self, max_messages=10):
        self.messages = []
        self.max_messages = max_messages

    def add_message(self, role, content):
        """
        Add a message to the conversation.
        """

        self.messages.append(
            {
                "role": role,
                "content": content
            }
        )

        # Keep only the most recent messages.
        self.messages = self.messages[
            -self.max_messages:
        ]

    def add_user_message(self, content):
        self.add_message(
            "user",
            content
        )

    def add_assistant_message(self, content):
        self.add_message(
            "assistant",
            content
        )

    def get_messages(self):
        """
        Return the stored messages.
        """

        return self.messages.copy()

    def get_formatted_history(self):
        """
        Return conversation history as text.
        """

        if not self.messages:
            return "No previous conversation."

        history = []

        for message in self.messages:

            role = message["role"].upper()

            history.append(
                f"{role}: {message['content']}"
            )

        return "\n".join(history)

    def clear(self):
        """
        Clear the current conversation.
        """

        self.messages.clear()