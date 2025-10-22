import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import calendar
import json
import os

# 페이지 설정
st.set_page_config(page_title="팀 일정 관리", page_icon="📅", layout="wide")

# 데이터 저장 경로
DATA_FILE = "team_schedules.json"

# 세션 상태 초기화
if 'current_date' not in st.session_state:
    st.session_state.current_date = datetime.now()
if 'selected_member' not in st.session_state:
    st.session_state.selected_member = 'all'
if 'view' not in st.session_state:
    st.session_state.view = 'calendar'
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'show_add_modal' not in st.session_state:
    st.session_state.show_add_modal = False

# 데이터 로드/저장 함수
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'members': [
            {"id": "1", "name": "부세미", "total_leave": 15, "used_leave": 0, "color": "#3B82F6"},
            {"id": "2", "name": "신사장", "total_leave": 15, "used_leave": 0, "color": "#10B981"},
            {"id": "3", "name": "백혜지", "total_leave": 15, "used_leave": 0, "color": "#F59E0B"}
        ],
        'schedules': []
    }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 데이터 로드
data = load_data()
members = data['members']
schedules = data['schedules']

# CSS 스타일
st.markdown("""
<style>
.schedule-item {
    padding: 6px;
    margin: 2px 0;
    border-radius: 4px;
    font-size: 0.8em;
}
</style>
""", unsafe_allow_html=True)

# 헤더
st.title("📅 팀 일정 관리 시스템")

# 탭 메뉴
col1, col2, col3, col4 = st.columns([2, 2, 2, 6])
with col1:
    if st.button("📅 캘린더", use_container_width=True):
        st.session_state.view = 'calendar'
        st.rerun()
with col2:
    if st.button("📊 통계", use_container_width=True):
        st.session_state.view = 'stats'
        st.rerun()
with col3:
    if st.button("👥 팀원", use_container_width=True):
        st.session_state.view = 'members'
        st.rerun()

st.markdown("---")

# 알림
if st.session_state.notifications:
    for i, notif in enumerate(st.session_state.notifications):
        col1, col2 = st.columns([10, 1])
        with col1:
            st.warning(f"⚠️ {notif}")
        with col2:
            if st.button("✕", key=f"close_{i}"):
                st.session_state.notifications.pop(i)
                st.rerun()

# 캘린더 뷰
if st.session_state.view == 'calendar':
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 3, 2, 2])
    
    with col1:
        if st.button("◀"):
            st.session_state.current_date -= timedelta(days=30)
            st.rerun()
    with col2:
        if st.button("오늘"):
            st.session_state.current_date = datetime.now()
            st.rerun()
    with col3:
        if st.button("▶"):
            st.session_state.current_date += timedelta(days=30)
            st.rerun()
    with col4:
        st.markdown(f"### {st.session_state.current_date.year}년 {st.session_state.current_date.month}월")
    with col5:
        member_options = ['전체'] + [m['name'] for m in members]
        selected_name = st.selectbox("팀원", member_options)
        st.session_state.selected_member = 'all' if selected_name == '전체' else next((m['id'] for m in members if m['name'] == selected_name), 'all')
    with col6:
        if st.button("➕ 일정 추가", type="primary"):
            st.session_state.show_add_modal = not st.session_state.show_add_modal

    # 일정 추가 폼
    if st.session_state.show_add_modal:
        st.markdown("### ➕ 일정 추가")
        col1, col2 = st.columns(2)
        with col1:
            selected_member_name = st.selectbox("팀원 선택", [m['name'] for m in members], key='add_member')
            schedule_type = st.selectbox("유형", ["연차", "반차", "병가", "출장", "재택근무"])
        with col2:
            schedule_date = st.date_input("날짜", value=datetime.now())
            reason = st.text_area("사유", height=80)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("추가", type="primary", use_container_width=True):
                selected_member = next((m for m in members if m['name'] == selected_member_name), None)
                if selected_member:
                    new_schedule = {
                        'id': str(int(datetime.now().timestamp() * 1000)),
                        'member_id': selected_member['id'],
                        'type': schedule_type,
                        'date': schedule_date.strftime('%Y-%m-%d'),
                        'reason': reason
                    }
                    schedules.append(new_schedule)
                    
                    # 연차 업데이트
                    if schedule_type in ['연차', '반차']:
                        days = 0.5 if schedule_type == '반차' else 1.0
                        for m in members:
                            if m['id'] == selected_member['id']:
                                m['used_leave'] += days
                    
                    # 충돌 확인
                    conflicts = [s for s in schedules if s['date'] == new_schedule['date'] and s['member_id'] != new_schedule['member_id']]
                    if len(conflicts) >= 2:
                        st.session_state.notifications.append(f"{new_schedule['date']}에 {len(conflicts) + 1}명이 휴가입니다.")
                    
                    save_data({'members': members, 'schedules': schedules})
                    st.session_state.show_add_modal = False
                    st.success("일정이 추가되었습니다!")
                    st.rerun()
        with col2:
            if st.button("취소", use_container_width=True):
                st.session_state.show_add_modal = False
                st.rerun()

    st.markdown("---")
    
    # 캘린더 그리드
    year = st.session_state.current_date.year
    month = st.session_state.current_date.month
    first_day = datetime(year, month, 1)
    first_weekday = (first_day.weekday() + 1) % 7
    days_in_month = calendar.monthrange(year, month)[1]
    
    # 요일 헤더
    days_header = ['일', '월', '화', '수', '목', '금', '토']
    cols = st.columns(7)
    for i, day in enumerate(days_header):
        with cols[i]:
            st.markdown(f"**{day}**")
    
    # 날짜 그리드
    current_day = 1
    week = 0
    while current_day <= days_in_month:
        cols = st.columns(7)
        for col_idx in range(7):
            with cols[col_idx]:
                if week == 0 and col_idx < first_weekday:
                    st.markdown("&nbsp;")
                elif current_day <= days_in_month:
                    date_str = f"{year}-{month:02d}-{current_day:02d}"
                    day_schedules = [s for s in schedules if s['date'] == date_str]
                    if st.session_state.selected_member != 'all':
                        day_schedules = [s for s in day_schedules if s['member_id'] == st.session_state.selected_member]
                    
                    st.markdown(f"**{current_day}**")
                    
                    for schedule in day_schedules[:2]:
                        member = next((m for m in members if m['id'] == schedule['member_id']), None)
                        if member:
                            st.markdown(f'<div class="schedule-item" style="background-color: {member["color"]}20; border-left: 3px solid {member["color"]}"><b>{member["name"]}</b><br>{schedule["type"]}</div>', unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_{schedule['id']}"):
                                schedules.remove(schedule)
                                if schedule['type'] in ['연차', '반차']:
                                    days = 0.5 if schedule['type'] == '반차' else 1.0
                                    for m in members:
                                        if m['id'] == schedule['member_id']:
                                            m['used_leave'] = max(0, m['used_leave'] - days)
                                save_data({'members': members, 'schedules': schedules})
                                st.rerun()
                    
                    if len(day_schedules) > 2:
                        st.caption(f"+{len(day_schedules) - 2}")
                    current_day += 1
        week += 1

# 통계 뷰
elif st.session_state.view == 'stats':
    st.markdown("## 📊 통계")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("팀원", f"{len(members)}명")
    with col2:
        avg_used = sum(m['used_leave'] for m in members) / len(members) if members else 0
        st.metric("평균 연차 사용", f"{avg_used:.1f}일")
    with col3:
        st.metric("총 일정", f"{len(schedules)}건")
    
    st.markdown("---")
    
    for member in members:
        remaining = member['total_leave'] - member['used_leave']
        percentage = (member['used_leave'] / member['total_leave']) * 100 if member['total_leave'] > 0 else 0
        st.markdown(f"**{member['name']}**: {member['used_leave']}/{member['total_leave']}일 ({remaining}일 남음)")
        st.progress(percentage / 100)

# 팀원 관리 뷰
elif st.session_state.view == 'members':
    st.markdown("## 👥 팀원 관리")
    
    for member in members:
        col1, col2, col3 = st.columns([1, 4, 2])
        with col1:
            st.markdown(f'<div style="width:30px;height:30px;background:{member["color"]};border-radius:5px"></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{member['name']}**")
        with col3:
            st.caption(f"{member['used_leave']}/{member['total_leave']}일")
    
    st.markdown("---")
    st.markdown("### 팀원 추가")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        new_name = st.text_input("이름")
    with col2:
        new_leave = st.number_input("연차", min_value=0, value=15)
    with col3:
        colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
        new_color = st.selectbox("색상", colors)
    
    if st.button("추가", type="primary"):
        if new_name:
            members.append({
                'id': str(int(datetime.now().timestamp() * 1000)),
                'name': new_name,
                'total_leave': new_leave,
                'used_leave': 0,
                'color': new_color
            })
            save_data({'members': members, 'schedules': schedules})
            st.success(f"{new_name}님 추가!")
            st.rerun()

st.markdown("---")
st.caption(f"팀 일정 관리 시스템 | {datetime.now().strftime('%Y-%m-%d')}")
