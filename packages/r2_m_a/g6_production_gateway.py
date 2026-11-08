"""Explicit G6 production gateway factory using the approved artificial F_aff source.

This is an engineering source determined by the sealed G5 law ID, not an
independent hidden scientific oracle. The gateway releases public P and allows
one paid Q001; no production GO, execution, scoring, or digest authority is
created by constructing it.
"""
from __future__ import annotations

from packages.r2_m_eng.source_gateway import PublicGateway, SyntheticPrivateSource

from .contracts import LAW_IDS
from .g6_order import G6Blocked


def production_gateway_factory(law: str, at: int) -> PublicGateway:
    """Build a fresh public gateway for one validated G5 law and opening time.

    This is passed explicitly as G6Driver(..., gateway_factory=...).
    METHOD/POLICY digests are NOT parameters: G6QStage obtains them exclusively
    from the frozen anchors in g6_q.QArtifactFiles.digests().
    """
    if type(law) is not str or law not in LAW_IDS:
        raise G6Blocked("RUN_BLOCK: invalid production law ID")
    if type(at) is not int or at < 0:
        raise G6Blocked("RUN_BLOCK: invalid production gateway opening time")

    coefficients = tuple(int(bit) for bit in law)
    return PublicGateway(
        SyntheticPrivateSource(coefficients),
        opened_at=at,
        expires_at=at + 900,
    )
