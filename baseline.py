from langchain_ollama import OllamaLLM

# Initialize model
model = OllamaLLM(model="llama3", temperature=0)


def baseline(text):
    """
    Raw LLM output (no guidance)
    """
    try:
        return model.invoke(text)
    except Exception as e:
        return f"Error in baseline: {e}"


def improved(text):
    """
    Prompt-engineered output (better extraction)
    """
    try:
        prompt = f"""
        You are an information extraction system.

        Extract ONLY the key information from the text below.
        Do not add explanations.

        TEXT:
        {text}
        """

        return model.invoke(prompt)

    except Exception as e:
        return f"Error in improved: {e}"


def run_comparison(sample_text):
    """
    Runs both baseline and improved methods
    """
    print("\n===== BASELINE OUTPUT =====")
    base = baseline(sample_text)
    print(base)

    print("\n===== IMPROVED OUTPUT =====")
    imp = improved(sample_text)
    print(imp)

    return base, imp


# 🔥 Test sample
if __name__ == "__main__":
    sample = "AI is widely used in healthcare, finance, and autonomous vehicles."

    run_comparison(sample)