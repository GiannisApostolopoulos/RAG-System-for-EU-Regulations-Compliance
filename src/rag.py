
from LLM.retriever import Retriever


def main(question: str) -> str:

    retriever = Retriever()

    answer = retriever.ask(question)

    return answer["clean_answer"]


if __name__ == "__main__":

    # question = input("Enter your question: ")
    question = "What are some generic obligations of a company under EU laws?"
    answer = main(question)
    print(answer)