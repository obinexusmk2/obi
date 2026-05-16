"""Data-oriented probe adapter for functional and OOP probe forms."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional

import numpy as np

from .probe import external_probe, internal_probe, probe_alignment
from .types import Config, D, ProbeResult, S


ProbeCallable = Callable[..., ProbeResult]


@dataclass(frozen=True)
class FunctionalProbe:
    """Functional view over the canonical data-oriented probe logic."""

    internal: ProbeCallable
    external: ProbeCallable
    alignment: ProbeCallable
    logic: Mapping[str, ProbeCallable]

    def _to_dop(self) -> Mapping[str, ProbeCallable]:
        return self.logic


class DataProbeAdapter:
    """
    Data-Oriented Probe adapter.

    The adapter keeps the declarative probe logic as the source of truth and
    exposes equivalent functional and object-oriented forms.
    """

    def __init__(
        self,
        logic: Optional[Mapping[str, ProbeCallable]] = None,
        config: Optional[Config] = None,
    ) -> None:
        self.config = config or Config()
        self.logic: Dict[str, ProbeCallable] = {
            "internal": internal_probe,
            "external": external_probe,
            "alignment": probe_alignment,
        }
        if logic:
            self.logic.update(logic)
        self._validate(self.logic)

    def _validate(self, logic: Mapping[str, ProbeCallable]) -> None:
        required = ("internal", "external", "alignment")
        missing = [name for name in required if name not in logic]
        if missing:
            raise ValueError(f"DataProbeAdapter missing probe logic: {missing}")
        for name in required:
            if not callable(logic[name]):
                raise TypeError(f"DataProbeAdapter logic '{name}' must be callable")

    def to_functional(self) -> FunctionalProbe:
        """Return functional probe callables bound to this adapter config."""

        def internal(data: D, config: Optional[Config] = None) -> ProbeResult:
            return self.logic["internal"](data, config or self.config)

        def external(
            state: S,
            event: Optional[Dict[str, Any]] = None,
            output_shape: Optional[tuple] = None,
            config: Optional[Config] = None,
        ) -> ProbeResult:
            return self.logic["external"](
                state,
                event=event,
                output_shape=output_shape,
                config=config or self.config,
            )

        def alignment(
            data: D,
            state: S,
            config: Optional[Config] = None,
        ) -> ProbeResult:
            return self.logic["alignment"](data, state, config or self.config)

        return FunctionalProbe(
            internal=internal,
            external=external,
            alignment=alignment,
            logic=self.logic,
        )

    def to_oop(self):
        """Return a class-style probe object backed by the same logic."""
        logic = self.logic
        default_config = self.config

        class OOPProbe:
            _logic = logic

            def __init__(self, config: Optional[Config] = None) -> None:
                self.config = config or default_config

            def internal(self, data: D) -> ProbeResult:
                return logic["internal"](data, self.config)

            def external(
                self,
                state: S,
                event: Optional[Dict[str, Any]] = None,
                output_shape: Optional[tuple] = None,
            ) -> ProbeResult:
                return logic["external"](
                    state,
                    event=event,
                    output_shape=output_shape,
                    config=self.config,
                )

            def alignment(self, data: D, state: S) -> ProbeResult:
                return logic["alignment"](data, state, self.config)

            @classmethod
            def _to_dop(cls) -> Mapping[str, ProbeCallable]:
                return cls._logic

        return OOPProbe

    def verify_bijection(self, data: D, state: S) -> Dict[str, Any]:
        """Verify functional and OOP probes agree for the same inputs."""
        functional = self.to_functional()
        OOPProbe = self.to_oop()
        oop = OOPProbe()

        f_internal = functional.internal(data)
        o_internal = oop.internal(data)
        f_external = functional.external(state)
        o_external = oop.external(state)
        f_alignment = functional.alignment(data, state)
        o_alignment = oop.alignment(data, state)

        equivalent = (
            _same_result(f_internal, o_internal)
            and _same_result(f_external, o_external)
            and _same_result(f_alignment, o_alignment)
        )

        return {
            "equivalent": equivalent,
            "functional": {
                "internal": f_internal,
                "external": f_external,
                "alignment": f_alignment,
            },
            "oop": {
                "internal": o_internal,
                "external": o_external,
                "alignment": o_alignment,
            },
        }


def _same_result(left: ProbeResult, right: ProbeResult) -> bool:
    if left.channel != right.channel:
        return False
    if not np.isclose(left.confidence, right.confidence):
        return False
    if not np.array_equal(left.state, right.state):
        return False
    if left.data is None or right.data is None:
        return left.data is None and right.data is None
    return np.array_equal(left.data, right.data)
