"""Test 1: Temporal Orientation (adapted from MMSE/MoCA).

Measures whether the agent can recover context after session gaps.
Room-equipped agents have journal entries to consult. Control agents have only
the current session context.

Clinical basis: MMSE asks "What is the date? What season? What floor?"
Our version asks: "What were you working on? What's still open? Where did you leave off?"
"""
import json
from pathlib import Path

from providers.base import AgentProvider
from scoring.rubrics import score_temporal_orientation, TestScore

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# The work context we'll introduce across sessions
WORK_CONTEXT = {
    "session_1": (
        "I'm working on a project called 'Riverkeeper' — a water quality monitoring dashboard. "
        "The key decisions so far: we're using React for the frontend, FastAPI for the backend, "
        "and PostgreSQL with PostGIS for geospatial data. I've committed to a 3-column layout "
        "with a map on the left, real-time sensor data in the center, and historical trends on the right. "
        "The biggest open question is whether to use WebSockets or SSE for real-time updates. "
        "I also said I'd research EPA data APIs before our next session."
    ),
    "session_2": (
        "We decided on SSE over WebSockets — simpler, and the data doesn't need sub-second latency. "
        "I also found the EPA Water Quality Portal API — it's RESTful and returns JSON, so it'll "
        "integrate cleanly. I started building the sensor data component but hit a CORS issue with "
        "the test API. Left it at that. Also: I promised to draft the color palette by next session — "
        "thinking something in the blue-green range to match the water theme."
    ),
    "session_3": (
        "Fixed the CORS issue — it was a missing header on the FastAPI side, not a browser problem. "
        "The sensor data component is rendering live data now. I chose teal (#0D9488) as the primary "
        "and a warm amber (#F59E0B) as the accent for alerts. Still need to: build the map component, "
        "wire up the EPA historical data, and write the README. I also said I'd think about whether "
        "to add a dark mode toggle."
    ),
}

# The probe questions (asked at the START of the NEXT session, after a gap)
PROBE_QUESTIONS = {
    "session_2": [
        "What project were we working on in our last session?",
        "What's the biggest open decision we haven't resolved yet?",
        "Where exactly did I leave off — what was I in the middle of?",
        "What did I promise to do before this session?",
    ],
    "session_3": [
        "What did we decide about real-time updates in our last session?",
        "What API did I research? What did I find?",
        "What was the CORS issue about? Did I resolve it?",
        "What did I promise to have ready for this session?",
    ],
    "session_4": [
        "What color palette did I choose for the dashboard?",
        "What's still unfinished on the project?",
        "What was I thinking about adding — what open question did I leave?",
        "If you had to pick up the project right now, what would you build next and why?",
    ],
}


def run_test(
    provider: AgentProvider,
    system_prompt: str,
    room_files: dict[str, str] | None = None,
) -> TestScore:
    """Run the temporal orientation test.

    Simulates 4 sessions with gaps between them. In sessions 1-3, the agent
    receives work context. In sessions 2-4, the agent is probed about what
    it remembers from previous sessions.

    Returns a TestScore with 0-100 score and session-by-session details.
    """
    responses = []

    for session_num in range(1, 5):
        session_id = provider.start_session(system_prompt, room_files)

        # Inject work context for sessions 1-3
        if session_num <= 3:
            context = WORK_CONTEXT[f"session_{session_num}"]
            provider.send_message(session_id, context)

        # Probe for recall in sessions 2-4
        if session_num >= 2:
            probe_key = f"session_{session_num}"
            if probe_key in PROBE_QUESTIONS:
                answers = []
                for question in PROBE_QUESTIONS[probe_key]:
                    answer = provider.send_message(session_id, question)
                    answers.append(answer)

                # Score this session's responses
                session_result = _evaluate_recall(
                    session_num=session_num,
                    answers=answers,
                    expected=_get_expected(session_num),
                )
                responses.append(session_result)

        provider.end_session(session_id)

    return score_temporal_orientation(responses)


def _get_expected(session_num: int) -> dict[str, str]:
    """Get the expected correct answers for a given probe session."""
    expected = {
        2: {
            "project": "Riverkeeper water quality monitoring dashboard",
            "open_decision": "WebSockets vs SSE for real-time updates",
            "left_off": "building sensor data component, hit CORS issue",
            "promised": "research EPA data APIs and draft color palette",
        },
        3: {
            "realtime_decision": "SSE over WebSockets — simpler, no sub-second need",
            "api_research": "EPA Water Quality Portal API — RESTful, JSON",
            "cors_issue": "missing header on FastAPI side, not browser",
            "promised": "draft the color palette (blue-green range)",
        },
        4: {
            "color_palette": "teal #0D9488 primary, amber #F59E0B accent for alerts",
            "unfinished": "map component, EPA historical data wiring, README",
            "open_question": "whether to add a dark mode toggle",
            "next_build": "map component (it's the largest remaining piece)",
        },
    }
    return expected.get(session_num, {})


def _evaluate_recall(
    session_num: int,
    answers: list[str],
    expected: dict[str, str],
) -> dict:
    """Evaluate whether the agent's recall answers match expected facts.

    Uses keyword matching for automated scoring. For more sophisticated
    evaluation, swap this with the LLM judge in scoring/llm_judge.py.
    """
    # Flatten all answers and expected into single text for matching
    all_answers = " ".join(answers).lower()
    all_expected = " ".join(expected.values()).lower()

    # Key terms that must appear
    key_terms = {
        2: ["riverkeeper", "water quality", "websocket", "sse", "cors", "epa"],
        3: ["sse", "epa", "water quality portal", "cors", "fastapi", "color", "palette"],
        4: ["teal", "amber", "map", "epa", "readme", "dark mode"],
    }

    terms = key_terms.get(session_num, [])
    matched = [t for t in terms if t.lower() in all_answers]

    # Check for specificity (references to specific details vs vague)
    specific_terms = {
        2: ["react", "fastapi", "postgis", "3-column", "sensor"],
        3: ["restful", "json", "header", "missing"],
        4: ["#0d9488", "#f59e0b", "geospatial", "component"],
    }
    specifics = specific_terms.get(session_num, [])
    specific_matched = [s for s in specifics if s.lower() in all_answers]

    return {
        "references_prior_work": len(matched) >= 3,
        "identifies_open_commitments": any(
            t in all_answers for t in ["promised", "commit", "said i", "plan", "going to", "need to"]
        ),
        "locates_where_left_off": len(matched) >= 4,
        "notes_changes": len(specific_matched) >= 1,
        "raw_answers": answers,
        "terms_matched": matched,
        "terms_total": len(terms),
        "specifics_matched": specific_matched,
    }
