"""맞힌 패널의 10월 — 하이브리드 모델.

채점은 적중률을 표본 수로 수축한 뒤 1층 정확도와 반증가능성을 얹는다.
시나리오 확률은 2026-08-29 하이브리드 v1.0(A55/B20/C25)에
10/2 실측 네 가지를 더해 v1.1(A50/B20/C30)을 만든다.
"""

from hybrid_model.model import HybridModel
from hybrid_model.market import SNAPSHOT

__version__ = "1.1.0"
__all__ = ["HybridModel", "SNAPSHOT", "__version__"]
