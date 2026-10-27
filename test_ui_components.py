from pathlib import Path
import pandas as pd
from ui_components import (
    hero, metric_tile, decision_banner, decision_distribution,
    score_histogram, score_ring,
)

ROOT=Path(__file__).resolve().parent.parent


def test_html_escapes_untrusted_text():
    source='<script>alert("x")</script>'
    for html in [hero(source,'hi'),metric_tile(source,'1','ok'),decision_banner('Đề xuất duyệt',source)]:
        assert '<script>' not in html
        assert '&lt;script&gt;' in html


def test_no_plotly_import_in_app():
    source=(ROOT/'app.py').read_text(encoding='utf-8')
    assert 'import plotly' not in source
    assert (ROOT/'style.css').exists()


def test_donut_counts_match_group_file():
    data=pd.read_csv(ROOT/'momo_loan_simulation_results.csv')
    counts=data['Decision'].value_counts()
    assert len(data)==2000
    assert int(counts.get('Đề xuất duyệt'))==740
    assert int(counts.get('Đề xuất từ chối theo quy tắc mô phỏng'))==1014
    assert counts.sum()==2000
    html=decision_distribution(counts)
    assert '2,000' in html
    assert '740' in html


def test_histogram_and_score_ring_render():
    data=pd.read_csv(ROOT/'momo_loan_simulation_results.csv')
    html=score_histogram(data['S_final'])
    assert html.count('w365-hist-col')==12
    ring=score_ring(80.25)
    assert '80.2' in ring
    assert 'conic-gradient' in ring
