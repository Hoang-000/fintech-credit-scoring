"""Small HTML components for a Workspace 365-inspired light theme.

All HTML generated here is presentation-only; native Streamlit widgets stay interactive.
No external images, browser scripts, or third-party chart libraries are required.
"""
from html import escape
from math import isfinite
import numpy as np


def h(text):
    return escape(str(text), quote=True)


def brand():
    return '''<div class="w365-brand">
      <div class="w365-emblem"><i></i><i></i><i></i><i></i></div>
      <div><div class="w365-brand-name">FinLab <span style="font-weight:500">Credit</span></div>
      <div class="w365-brand-sub">HỌC VIỆN NGÂN HÀNG · FINTECH</div></div>
    </div>'''


def hero(title, description, label="DEMO HỌC THUẬT · AI + BIG DATA"):
    return f'''<section class="w365-hero">
      <div class="w365-hero-left"><div class="w365-eyebrow">{h(label)}</div>
        <h1>{h(title)}</h1><p>{h(description)}</p>
      </div>
      <div class="w365-hero-right"><div class="w365-hero-orbit"><strong>AI × DATA</strong>
      <span>CREDIT SCORING</span></div></div>
    </section>'''


def page_heading(title, subtitle="", tag="NGHIÊN CỨU / DEMO"):
    return f'''<div class="w365-page-head"><div><h2>{h(title)}</h2>
      <p>{h(subtitle)}</p></div><span class="w365-tag">{h(tag)}</span></div>'''


def metric_tile(label, value, note, icon="◆"):
    return f'''<div class="w365-kpi"><div class="w365-kpi-top">
        <span>{h(label)}</span><span class="w365-kpi-icon">{h(icon)}</span></div>
        <div class="w365-kpi-value">{h(value)}</div>
        <div class="w365-kpi-meta">{h(note)}</div></div>'''


def decision_distribution(counts):
    values = [int(counts.get(x, 0)) for x in (
        'Đề xuất duyệt',
        'Xem xét thêm / Chờ bổ sung thông tin',
        'Xem xét thêm',
        'Đề xuất từ chối theo quy tắc mô phỏng',
    )]
    approved, pending, review, rejected = values
    n = max(1, sum(values))
    ap = 100 * approved / n
    rv = 100 * (pending + review) / n
    gradient = (f'conic-gradient(#D90A63 0% {ap:.3f}%, '
                f'#EEB547 {ap:.3f}% {ap+rv:.3f}%, '
                f'#5A285D {ap+rv:.3f}% 100%)')
    legends = [
        ('#D90A63', 'Đề xuất duyệt', approved),
        ('#EEB547', 'Xem xét thêm', pending + review),
        ('#5A285D', 'Đề xuất từ chối', rejected),
    ]
    legend_html = ''.join(
        f'''<div class="w365-legend-row"><span class="w365-legend-left">
        <i class="w365-legend-dot" style="background:{color}"></i>{h(label)}</span>
        <b>{value:,}</b></div>''' for color,label,value in legends
    )
    return f'''<div class="w365-panel"><div class="w365-panel-title">Phân loại hồ sơ</div>
      <div class="w365-panel-sub">Kết quả đã lưu từ 2.000 hồ sơ giả lập</div>
      <div class="w365-donut-wrap"><div class="w365-donut" style="background:{gradient}">
      <div class="w365-donut-inner"><b>{sum(values):,}</b><small>hồ sơ</small></div></div>
      <div class="w365-legend">{legend_html}</div></div></div>'''


def score_histogram(scores):
    data = np.asarray(scores, dtype=float)
    data = data[np.isfinite(data)]
    counts, _ = np.histogram(data, bins=12, range=(0,100))
    max_count = max(1, max(counts))
    parts=[]
    for i,v in enumerate(counts):
        label = f'{i*100/12:.0f}–{(i+1)*100/12:.0f}'
        height=max(2.5, float(v)/max_count*100)
        parts.append(f'''<div class="w365-hist-col" title="Điểm {h(label)}: {v:,} hồ sơ"
        aria-label="Điểm {h(label)}: {v:,} hồ sơ"><div class="w365-hist-bar"
        style="height:{height:.2f}%"></div></div>''')
    return f'''<div class="w365-panel"><div class="w365-panel-title">Phân phối điểm tổng hợp</div>
      <div class="w365-panel-sub">Điểm S_final của các hồ sơ trong bộ dữ liệu</div>
      <div class="w365-histogram">{''.join(parts)}</div>
      <div class="w365-axis"><span>0</span><span>25</span><span>50</span><span>75</span><span>100 điểm</span></div></div>'''


def decision_banner(decision, reason):
    label=str(decision)
    if label=='Đề xuất duyệt':
        style='good'; heading='Hồ sơ được đề xuất duyệt'
    elif label.startswith('Xem xét thêm'):
        style='review'; heading='Hồ sơ cần xem xét thêm'
    else:
        style='reject'; heading='Hồ sơ được đề xuất từ chối'
    return f'''<div class="w365-result {style}">
      <div class="w365-kicker">KẾT QUẢ MÔ PHỎNG · KHÔNG PHẢI QUYẾT ĐỊNH CHO VAY</div>
      <div class="w365-result-title">{h(heading)}</div>
      <div class="w365-result-desc">{h(reason)}</div></div>'''


def score_ring(score, title='S_final'):
    score = float(score)
    if not isfinite(score): score=0.0
    score = max(0.0,min(100.0,score))
    degree=round(score/100*360,2)
    return f'''<div class="w365-score-ring" style="background:
       conic-gradient(#D90A63 0deg {degree}deg, #F6E4ED {degree}deg 360deg)">
       <div class="w365-score-inner"><b>{score:.1f}</b><small>{h(title)} / 100</small></div></div>'''


def workflow_steps():
    steps=[
        ('01','Tiếp nhận hồ sơ','Nhập thông tin vay và trạng thái eKYC'),
        ('02','Kiểm tra điều kiện','Tuổi, CIC, DTI và quy tắc R01–R10'),
        ('03','Dự đoán bằng AI','Pipeline Home Credit và Logistic Regression'),
        ('04','Ra đề xuất','Tổng hợp điểm AI, điểm quy tắc và ngưỡng'),
    ]
    return '<div class="w365-process">'+''.join(
        f'<div class="w365-process-item"><span class="w365-process-num">{h(num)}</span>'
        f'<b>{h(title)}</b><p>{h(text)}</p></div>' for num,title,text in steps
    )+'</div>'


def disclaimer(text):
    return f'<div class="w365-disclaimer">{h(text)}</div>'


def footer():
    return '''<div class="w365-footer"><span>FinLab Credit · Công nghệ dịch vụ tài chính</span>
      <span>Dữ liệu giả lập · Home Credit nghiên cứu · Không liên kết MoMo</span></div>'''
