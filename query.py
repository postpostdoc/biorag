import torch
from llama_index.llms import Ollama

# Set device to CPU explicitly
# device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")

from ragatouille import RAGPretrainedModel

rag = RAGPretrainedModel.from_index(".ragatouille/colbert/indexes/muscle_sample/")


def get_snippets(query):
    docs = rag.search(query)
    return [doc for doc in docs]


def concatenate_snippets(snippet_dicts):
    concatenated = {}
    for snippet in snippet_dicts:
        document_id = snippet['document_id']
        content = snippet['content']
        if document_id in concatenated:
            concatenated[document_id]['content'] += content
        else:
            concatenated[document_id] = {'content': content, 'document_id': document_id}
    return concatenated


def print_snippets(docs):
    print("Found", len(docs), "documents")
    for doc in docs:
        text = doc['content']
        print(text[:1000] + "..." if len(text) > 1000 else text)
        print('---------')


def llm_call(query, context):
    llm = Ollama(model="zephyr", base_url="http://127.0.0.1:11434/")

    prompt = """
    The user asks the following query: "%s"
    
    You need to output only "YES" or "NO" as an answer to the following question: 
    
    "Does the provided document text provide support or counterargument for the user query?"
    
    The document text is the following:
    %s
    """

    res = llm.complete(prompt.format(query, context))
    return res


def forever_user_input():
    while 1:
        user_input = input("Enter your search query: ")
        snippets = get_snippets(user_input)
        # print_snippets(docs)
        context = concatenate_snippets(snippets)
        for doc_id, content in context.items():
            res = llm_call(user_input, context)


def main():
    forever_user_input()


if __name__ == '__main__':
    main()
