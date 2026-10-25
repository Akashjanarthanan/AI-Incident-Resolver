from conversation_memory import ConversationMemory


def main():

    memory = ConversationMemory()

    memory.add_user_message(
        "Application cannot connect to Oracle."
    )

    memory.add_assistant_message(
        "Check whether the Oracle listener is running."
    )

    memory.add_user_message(
        "The listener is already running."
    )

    print("\nConversation History:")
    print(
        memory.get_formatted_history()
    )


if __name__ == "__main__":
    main()