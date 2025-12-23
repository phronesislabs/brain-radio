"""Supervisor Agent: Orchestrates the agent workflow using LangGraph."""

from typing import TypedDict

from langgraph.graph import END, StateGraph
from langchain_openai import ChatOpenAI

from brain_radio.agents.neuro_composer import NeuroComposerAgent
from brain_radio.agents.researcher import ResearcherAgent
from brain_radio.models import (
    PlaylistRequest,
    PlaylistResult,
    ProtocolConstraints,
    TrackMetadata,
    VerificationResult,
)


class SupervisorState(TypedDict):
    """State managed by Supervisor agent."""

    request: PlaylistRequest
    constraints: ProtocolConstraints | None
    candidate_tracks: list[TrackMetadata]
    verified_tracks: list[VerificationResult]
    approved_tracks: list[TrackMetadata]
    result: PlaylistResult | None
    error: str | None


class SupervisorAgent:
    """
    Supervisor Agent (The "Orchestrator").

    Owns the end-to-end run. Routes work to worker agents, enforces invariants,
    and produces auditable outputs.
    """

    def __init__(self, llm: ChatOpenAI | None = None):
        """Initialize Supervisor agent."""
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.neuro_composer = NeuroComposerAgent()
        self.researcher = ResearcherAgent(llm=llm)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow."""
        workflow = StateGraph(SupervisorState)

        # Add nodes
        workflow.add_node("compose_constraints", self._compose_constraints)
        workflow.add_node("generate_candidates", self._generate_candidates)
        workflow.add_node("verify_tracks", self._verify_tracks)
        workflow.add_node("filter_approved", self._filter_approved)
        workflow.add_node("build_result", self._build_result)

        # Define edges
        workflow.set_entry_point("compose_constraints")
        workflow.add_edge("compose_constraints", "generate_candidates")
        workflow.add_edge("generate_candidates", "verify_tracks")
        workflow.add_edge("verify_tracks", "filter_approved")
        workflow.add_edge("filter_approved", "build_result")
        workflow.add_edge("build_result", END)

        return workflow.compile()

    async def generate_playlist(self, request: PlaylistRequest) -> PlaylistResult:
        """
        Generate a playlist using the agent workflow.

        Args:
            request: Playlist generation request

        Returns:
            PlaylistResult with approved tracks
        """
        initial_state: SupervisorState = {
            "request": request,
            "constraints": None,
            "candidate_tracks": [],
            "verified_tracks": [],
            "approved_tracks": [],
            "result": None,
            "error": None,
        }

        final_state = await self.graph.ainvoke(initial_state)

        if final_state.get("error"):
            raise RuntimeError(f"Supervisor error: {final_state['error']}")

        if not final_state.get("result"):
            raise RuntimeError("Supervisor did not produce a result")

        return final_state["result"]

    async def _compose_constraints(self, state: SupervisorState) -> SupervisorState:
        """Compose protocol constraints."""
        request = state["request"]
        constraints = self.neuro_composer.compose_constraints(
            mode=request.mode, genre=request.genre
        )
        state["constraints"] = constraints
        return state

    async def _generate_candidates(self, state: SupervisorState) -> SupervisorState:
        """
        Generate candidate tracks.

        TODO: This should use Spotify Catalog Agent to search for tracks.
        For now, we'll use mock candidates for testing.
        """
        # Mock implementation - in production, this would use Spotify API
        constraints = state["constraints"]
        if not constraints:
            state["error"] = "Constraints not composed"
            return state

        # Mock candidate tracks (will be replaced with real Spotify search)
        state["candidate_tracks"] = []
        return state

    async def _verify_tracks(self, state: SupervisorState) -> SupervisorState:
        """Verify all candidate tracks."""
        constraints = state["constraints"]
        if not constraints:
            state["error"] = "Constraints not composed"
            return state

        verified: list[VerificationResult] = []
        for track in state["candidate_tracks"]:
            result = await self.researcher.verify_track(track, constraints)
            verified.append(result)

        state["verified_tracks"] = verified
        return state

    async def _filter_approved(self, state: SupervisorState) -> SupervisorState:
        """Filter to only approved tracks."""
        approved = [vr.track for vr in state["verified_tracks"] if vr.approved]
        state["approved_tracks"] = approved
        return state

    async def _build_result(self, state: SupervisorState) -> SupervisorState:
        """Build final playlist result."""
        request = state["request"]
        approved = state["approved_tracks"]

        total_duration = sum(t.duration_ms or 0 for t in approved)

        verification_summary = {
            "total_candidates": len(state["candidate_tracks"]),
            "approved": len(approved),
            "rejected": len(state["verified_tracks"]) - len(approved),
        }

        result = PlaylistResult(
            mode=request.mode,
            tracks=approved,
            total_duration_ms=total_duration,
            verification_summary=verification_summary,
        )

        state["result"] = result
        return state
