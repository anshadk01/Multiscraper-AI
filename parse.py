from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# 🔧 Improved prompt (clearer + stricter)
template = (
    "You are an information extraction system.\n\n"
    "TEXT:\n{dom_content}\n\n"
    "TASK:\nExtract ONLY the data that matches this description:\n{parse_description}\n\n"
    "RULES:\n"
    "- Do NOT add explanations\n"
    "- Do NOT rephrase\n"
    "- Do NOT include extra words\n"
    "- If nothing matches, return an empty string\n"
)

# 🔧 Better model config (more stable)
model = OllamaLLM(
    model="llama3",
    temperature=0,      # deterministic output
)

def parse_with_ollama(dom_chunks, parse_description):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    parsed_results = []

    for i, chunk in enumerate(dom_chunks, start=1):
        try:
            # 🔧 limit chunk size (prevents overload)
            chunk = chunk[:3000]

            response = chain.invoke(
                {
                    "dom_content": chunk,
                    "parse_description": parse_description,
                }
            )

            # 🔧 clean response
            if response:
                cleaned = response.strip()
                if cleaned:
                    parsed_results.append(cleaned)

            print(f"Parsed batch: {i}/{len(dom_chunks)}")

        except Exception as e:
            print(f"Error in batch {i}: {e}")
            continue

    # 🔧 remove duplicates + clean join
    final_result = "\n".join(list(dict.fromkeys(parsed_results)))

    return final_result