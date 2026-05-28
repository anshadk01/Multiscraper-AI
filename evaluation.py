from rouge_score import rouge_scorer

def evaluate(reference, generated):
    scorer = rouge_scorer.RougeScorer(
        ['rouge1', 'rougeL'], 
        use_stemmer=True
    )

    scores = scorer.score(reference, generated)

    return scores