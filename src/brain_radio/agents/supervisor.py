"""Supervisor agent orchestrating the verification workflow."""

from __future__ import annotations

from typing import Sequence

from langgraph.graph import StateGraph
from pydantic import BaseModel

from brain_radio.agents.neuro_composer import Mode, NeuroComposer, ProtocolConstraints
from brain_radio.agents.researcher import (
    Researcher,
    TrackCandidate,
    VerificationDecision,
)


class SupervisorState(BaseModel):
    mode: Mode
    constraints: ProtocolConstraints
    candidates: list[TrackCandidate]
    decisions: list[VerificationDecision] = []


class Supervisor:
    """Routes tasks through the verification pipeline."""

    def __init__(
        self, researcher: Researcher, composer: NeuroComposer | None = None
    ) -> None:
        self._researcher = researcher
        self._composer = composer or NeuroComposer()

    def build_graph(self) -> StateGraph:
        graph = StateGraph(SupervisorState)
        graph.add_node("compose_constraints", self._compose_constraints)
        graph.add_node("verify_tracks", self._verify_tracks)
        graph.set_entry_point("compose_constraints")
        graph.add_edge("compose_constraints", "verify_tracks")
        graph.set_finish_point("verify_tracks")
        return graph

    def run(
        self, mode: Mode, candidates: Sequence[TrackCandidate]
    ) -> list[VerificationDecision]:
        constraints = self._composer.compose(mode)
        return [
            self._researcher.verify(candidate, constraints) for candidate in candidates
        ]

    def _compose_constraints(self, state: SupervisorState) -> SupervisorState:
        state.constraints = self._composer.compose(state.mode)
        return state

    def _verify_tracks(self, state: SupervisorState) -> SupervisorState:
        state.decisions = [
            self._researcher.verify(candidate, state.constraints)
            for candidate in state.candidates
        ]
        return state
