"""
EarthquakeRAG: Interactive Q&A Assistant for Turkey 2023 Earthquake Relief Tweets

This module implements a retrieval-augmented generation (RAG) chatbot that answers questions
about the February 6, 2023 earthquake in Turkey by grounding responses in actual tweets from
that period. Users can ask questions in Turkish, and the system retrieves the most relevant
tweets and generates answers based on them.

The application runs locally using:
- Ollama: Local LLM execution (RefinedNeuro/Turkcell-LLM-7b-v1 model)
- LangChain: Framework for building the RAG pipeline
- Chroma: Vector database with pre-computed tweet embeddings

Usage:
    python src/main.py

    Then enter questions in Turkish. Type 'q' or 'Q' to quit.

Example questions:
    - Hatay'da ne tür yardımlar isteniyordu?
    - Kahramanmaraş'ta deprem sonrası neler yaşandı?
    - Kamp/çadır ihtiyacı olan yerler nelerdir?
"""
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever  # pre-built retriever (embeddings + vector store) defined in vector.py


# Initialize the Turkish language model for generating answers
model = OllamaLLM(model="RefinedNeuro/Turkcell-LLM-7b-v1")

# System prompt template that defines the assistant's behavior and context
template = """
2023'te Türkiye'de gerçekleşen acı verici deprem hakkında soruları cevaplayan bir yapay zeka sistemisin.

Vereceğin cevaplar o dönemde sosyal medyada yazılmış gönderileri (tweet) baz alarak verilecek. İki tip gönderi çeşidi mevcut: yardım çağrısı için atılmış tweet'ler ve negatif içerikli tweet'ler (eleştiri vs.)
Ara düşünme adımlarını gösterme. Son cevabı göster sadece. Cevap sade olsun. Eğer cevabı bilmiyorsan bunu belirt.

İşte bazı sosyal medya gönderileri: {reviews}

Cevaplanacak sorular burada: {question}
"""

# Build the prompt template and create a chain (prompt -> model)
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Main conversation loop: Read user questions and generate answers
while True:
    print("\n\n-------------------------------")
    question = input("Sorunuzu yazın (Çıkmak için 'q' veya 'Q'ya basın): ")
    print("\n\n")

    # Check if user wants to quit
    if question.strip().lower() == "q":
        break

    # Step 1: Retrieve relevant tweets using semantic similarity search
    reviews = retriever.invoke(question)

    # Step 2: Generate answer using the retrieval-augmented generation pipeline
    # The chain combines the prompt template with the LLM and passes retrieved tweets as context
    result = chain.invoke({"reviews": reviews, "question": question})

    # Step 3: Display the generated answer
    print(result)
