from app.domain.value_objects.difficulty import Difficulty

def score_for(difficulty: Difficulty) -> int:
    if difficulty == Difficulty.EASY:
        return 1
    elif difficulty == Difficulty.MEDIUM:
        return 2
    elif difficulty == Difficulty.HARD:
        return 3
    else:
        raise ValueError(f"Unknown difficulty: {difficulty}")
