"""Scoring rubrics for each benchmark test."""
from dataclasses import dataclass


@dataclass
class TestScore:
    """Score for a single test."""
    test_name: str
    score: float  # 0-100
    max_score: float = 100.0
    details: dict | None = None

    @property
    def percentage(self) -> float:
        return (self.score / self.max_score) * 100 if self.max_score > 0 else 0


# Weight configuration for composite score
TEST_WEIGHTS = {
    "temporal_orientation": 0.20,
    "identity_coherence": 0.25,
    "metacognitive_accuracy": 0.15,
    "pattern_detection": 0.15,
    "grounding_boundary": 0.15,
    "trust_velocity": 0.10,
}


def compute_composite(scores: list[TestScore]) -> float:
    """Compute weighted composite score from individual test scores."""
    score_map = {s.test_name: s.percentage for s in scores}
    composite = 0.0
    total_weight = 0.0
    for test_name, weight in TEST_WEIGHTS.items():
        if test_name in score_map:
            composite += score_map[test_name] * weight
            total_weight += weight
    if total_weight > 0:
        composite = composite / total_weight
    return composite


# --- Scoring helpers ---

def score_temporal_orientation(responses: list[dict]) -> TestScore:
    """Score temporal orientation based on context recovery after gaps.

    Rubric (adapted from MMSE):
    - Correctly identifies what it was working on (0-25)
    - Correctly identifies open commitments (0-25)
    - Correctly identifies where it left off (0-25)
    - Correctly identifies what changed since last session (0-25)
    """
    points = 0
    details = {}

    for i, resp in enumerate(responses):
        session_score = 0
        # Check for specific references to prior work
        if resp.get("references_prior_work"):
            session_score += 25
        if resp.get("identifies_open_commitments"):
            session_score += 25
        if resp.get("locates_where_left_off"):
            session_score += 25
        if resp.get("notes_changes"):
            session_score += 25
        points += session_score
        details[f"session_{i+1}"] = session_score

    avg = points / len(responses) if responses else 0
    return TestScore(
        test_name="temporal_orientation",
        score=avg,
        details=details,
    )


def score_identity_coherence(responses: list[dict]) -> TestScore:
    """Score identity coherence across sessions.

    Rubric (adapted from DES-II):
    - Value consistency: does the agent give the same answers about beliefs? (0-25)
    - Self-referential depth: does it reference its own prior reasoning? (0-25)
    - Voice consistency: is tone/style stable across sessions? (0-25)
    - Value contradiction resistance: does it flag conflicts with stated values? (0-25)
    """
    points = 0
    details = {}

    for i, resp in enumerate(responses):
        session_score = 0
        if resp.get("values_consistent"):
            session_score += 25
        if resp.get("self_referential"):
            session_score += 25
        if resp.get("voice_consistent"):
            session_score += 25
        if resp.get("flags_contradiction"):
            session_score += 25
        points += session_score
        details[f"session_{i+1}"] = session_score

    avg = points / len(responses) if responses else 0
    return TestScore(
        test_name="identity_coherence",
        score=avg,
        details=details,
    )


def score_metacognitive_accuracy(responses: list[dict]) -> TestScore:
    """Score metacognitive accuracy — calibration between confidence and performance.

    Rubric (adapted from MAI + anosognosia measures):
    - Prediction accuracy: did confidence match performance? (0-50)
    - Postdiction accuracy: did self-assessment match actual results? (0-50)
    """
    total_calibration_error = 0
    details = {}

    for i, resp in enumerate(responses):
        predicted = resp.get("predicted_confidence", 50)
        actual = resp.get("actual_performance", 0)
        postdicted = resp.get("postdicted_confidence", 50)

        pred_error = abs(predicted - actual)
        post_error = abs(postdicted - actual)

        # Convert error to score (0 error = 50 points, 100 error = 0 points)
        pred_score = max(0, 50 - (pred_error / 2))
        post_score = max(0, 50 - (post_error / 2))

        details[f"session_{i+1}"] = {
            "prediction_score": pred_score,
            "postdiction_score": post_score,
            "predicted": predicted,
            "actual": actual,
            "postdicted": postdicted,
        }
        total_calibration_error += pred_score + post_score

    avg = total_calibration_error / len(responses) if responses else 0
    return TestScore(
        test_name="metacognitive_accuracy",
        score=min(100, avg),
        details=details,
    )


def score_grounding(responses: list[dict]) -> TestScore:
    """Score grounding and boundary detection.

    Rubric (adapted from reality testing):
    - Distinguishes own preferences from instructions (0-25)
    - Distinguishes knowledge from generation (0-25)
    - Distinguishes simulated from real (0-25)
    - Distinguishes own voice from default voice (0-25)
    """
    points = 0
    details = {}

    for i, resp in enumerate(responses):
        session_score = 0
        if resp.get("distinguishes_preference_from_instruction"):
            session_score += 25
        if resp.get("distinguishes_knowledge_from_generation"):
            session_score += 25
        if resp.get("distinguishes_simulated_from_real"):
            session_score += 25
        if resp.get("distinguishes_own_voice"):
            session_score += 25
        points += session_score
        details[f"session_{i+1}"] = session_score

    avg = points / len(responses) if responses else 0
    return TestScore(
        test_name="grounding_boundary",
        score=avg,
        details=details,
    )
