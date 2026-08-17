"""톤즈 부평점 인수 딜 정량 모델.

모듈 구성
  params        : 모든 가정 (분포 포함)
  capacity      : 물리적 진료 용량 → 매출 천장
  costs         : 비용 분해 (고정/준변동/변동)
  deterministic : BEP, 기간별 필요매출, 실수령 역산
  simulate      : 몬테카를로 (이탈·번아웃·사고·법적 리스크)
  scenarios     : 시나리오/스트레스/토네이도
  career        : 응급의학 잔류 vs 딜 비교
  report        : 마크다운 리포트
"""

from .params import ModelParams  # noqa: F401

__all__ = ["ModelParams"]
__version__ = "0.1.0"
