"""반도체 자료 전문을 읽어 투자 인사이트를 증류한다."""

__all__ = ["run"]


def run(inputs, out):
    from insight_distiller.pipeline import run as _run

    return _run(inputs, out)
