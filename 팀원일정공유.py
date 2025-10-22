import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import calendar
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import (
    load_members, add_schedule, delete_schedule, 
    add_member, get_member_by_id, check_conflicts, 
    get_statistics, load_schedules
)

st.set_page_config(page_title="팀 일정 관리", page_icon="📅", layout="wide")

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

members = load_members()
schedules = load_schedules()
stats = get_statistics()

st.markdown("""
<style>
.schedule-item {
    padding: 8px;
    margin: 4px 0;
    border-radius: 5px;
    font-size: 0.85em;
}
</style>
""", unsafe_allow_html=True)

st.title("📅 팀 일정 관리 시스템")

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
    if st.button("👥 팀원 관리", use_container_width=True):
        st.session_state.view = 'members'
        st.rerun()

st.markdown("---")

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
            st.session_state.current_date = st.session_state.current_date - timedelta(days=30)
            st.rerun()
    with col2:
        if st.button("오늘"):
            st.session_state.current_date = datetime.now()
            st.rerun()
    with col3:
        if st.button("▶"):
            st.session_state.current_date = st.session_state.current_date + timedelta(days=30)
            st.rerun()
    with col4:
        st.markdown(f"### {st.session_state.current_date.year}년 {st.session_state.current_date.month}월")
    with col5:
        member_options = ['전체 팀원'] + [m['name'] for m in members]
        selected_name = st.selectbox("팀원 필터", member_options)
        if selected_name == '전체 팀원':
            st.session_state.selected_member = 'all'
        else:
            selected = next((m for m in members if m['name'] == selected_name), None)
            st.session_state.selected_member = selected['id'] if selected else 'all'
    with col6:
        if st.button("➕ 일정 추가", type="primary"):
            st.session_state.show_add_modal = not st.session_state.show_add_modal

    if st.session_state.show_add_modal:
        with st.container():
            st.markdown("### ➕ 일정 추가")
            col1, col2 = st.columns(2)
            with col1:
                selected_member_name = st.selectbox("팀원", [m['name'] for m in members], key='add_member')
                schedule_type = st.selectbox("유형", ["연차", "반차", "병가", "출장", "재택근무"])
            with col2:
                schedule_date = st.date_input("날짜", value=datetime.now())
                reason = st.text_area("사유 (선택)", height=100)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("추가하기", type="primary", use_container_width=True):
                    selected_member = next((m for m in members if m['name'] == selected_member_name), None)
                    if selected_member:
                        new_schedule = {
                            'member_id': selected_member['id'],
                            'type': schedule_type,
                            'date': schedule_date.strftime('%Y-%m-%d'),
                            'reason': reason
                        }
                        add_schedule(new_schedule)
                        conflicts = check_conflicts(new_schedule['date'], new_schedule['member_id'])
                        if len(conflicts) >= 2:
                            st.session_state.notifications.append(
                                f"{new_schedule['date']}에 {len(conflicts) + 1}명이 휴가입니다."
                            )
                        st.session_state.show_add_modal = False
                        st.success("일정이 추가되었습니다!")
                        st.rerun()
            with col2:
                if st.button("취소", use_container_width=True):
                    st.session_state.show_add_modal = False
                    st.rerun()

    st.markdown("---")
    
    year = st.session_state.current_date.year
    month = st.session_state.current_date.month
    first_day = datetime(year, month, 1)
    first_weekday = first_day.weekday()
    if first_weekday == 6:
        first_weekday = 0
    else:
        first_weekday += 1
    days_in_month = calendar.monthrange(year, month)[1]
    
    days_header = ['일', '월', '화', '수', '목', '금', '토']
    cols = st.columns(7)
    for i, day in enumerate(days_header):
        with cols[i]:
            st.markdown(f"**{day}**")
    
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
                    
                    for schedule in day_schedules[:3]:
                        member = get_member_by_id(schedule['member_id'])
                        if member:
                            schedule_html = f"""
                            <div class="schedule-item" style="background-color: {member['color']}20; border-left: 3px solid {member['color']}">
                                <div style="font-weight: bold; font-size: 0.75em;">{member['name']}</div>
                                <div style="font-size: 0.7em; color: #666;">{schedule['type']}</div>
                            </div>
                            """
                            st.markdown(schedule_html, unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_{schedule['id']}", help="삭제"):
                                delete_schedule(schedule['id'])
                                st.rerun()
                    
                    if len(day_schedules) > 3:
                        st.caption(f"+{len(day_schedules) - 3}개")
                    current_day += 1
                else:
                    st.markdown("&nbsp;")
        week += 1

# 통계 뷰
elif st.session_state.view == 'stats':
    st.markdown("## 📊 통계 대시보드")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("전체 팀원", f"{stats['total_members']}명")
    with col2:
        st.metric("평균 사용 연차", f"{stats['avg_used_leave']:.1f}일")
    with col3:
        st.metric("총 일정 수", f"{stats['total_schedules']}건")
    with col4:
        most_common = max(stats['type_count'].items(), key=lambda x: x[1])[0] if stats['type_count'] else '-'
        st.metric("가장 많은 유형", most_common)
    
    st.markdown("---")
    st.markdown("### 👥 팀원별 연차 사용 현황")
    
    for member in members:
        remaining = member['total_leave'] - member['used_leave']
        percentage = (member['used_leave'] / member['total_leave']) * 100 if member['total_leave'] > 0 else 0
        col1, col2 = st.columns([3, 7])
        with col1:
            st.markdown(f"**{member['name']}**")
            st.caption(f"사용: {member['used_leave']}일 | 남은: {remaining}일 | 전체: {member['total_leave']}일")
        with col2:
            st.progress(percentage / 100)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 일정 유형별 현황")
        if stats['type_count']:
            type_df = pd.DataFrame([{'유형': k, '개수': v} for k, v in stats['type_count'].items()])
            fig = px.pie(type_df, values='개수', names='유형', hole=0.4)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("등록된 일정이 없습니다.")
    
    with col2:
        st.markdown("### 📈 월별 일정 추이")
        if schedules:
            schedule_df = pd.DataFrame(schedules)
            schedule_df['month'] = pd.to_datetime(schedule_df['date']).dt.to_period('M').astype(str)
            monthly_count = schedule_df.groupby('month').size().reset_index(name='count')
            fig = px.line(monthly_count, x='month', y='count', markers=True)
            fig.update_layout(xaxis_title="월", yaxis_title="일정 수", height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("등록된 일정이 없습니다.")
    
    st.markdown("---")
    st.markdown("### 📋 전체 일정 목록")
    if schedules:
        schedule_list = []
        for schedule in schedules:
            member = get_member_by_id(schedule['member_id'])
            schedule_list.append({
                '날짜': schedule['date'],
                '팀원': member['name'] if member else '알 수 없음',
                '유형': schedule['type'],
                '사유': schedule.get('reason', '-')
            })
        df = pd.DataFrame(schedule_list).sort_values('날짜', ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button("📥 CSV 다운로드", csv, f"팀일정_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
    else:
        st.info("등록된 일정이 없습니다.")

# 팀원 관리 뷰
elif st.session_state.view == 'members':
    st.markdown("## 👥 팀원 관리")
    st.markdown("### 현재 팀원")
    
    for member in members:
        col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
        with col1:
            st.markdown(f'<div style="width: 30px; height: 30px; background-color: {member["color"]}; border-radius: 5px;"></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{member['name']}**")
        with col3:
            st.caption(f"{member['used_leave']}/{member['total_leave']}일 사용")
        with col4:
            remaining = member['total_leave'] - member['used_leave']
            st.caption(f"남은: {remaining}일")
    
    st.markdown("---")
    st.markdown("### ➕ 팀원 추가")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        new_name = st.text_input("이름")
    with col2:
        new_total_leave = st.number_input("연차 일수", min_value=0, value=15, step=1)
    with col3:
        colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316']
        new_color = st.selectbox("색상", colors)
    
    if st.button("팀원 추가", type="primary"):
        if new_name:
            new_member = {'name': new_name, 'total_leave': new_total_leave, 'color': new_color}
            add_member(new_member)
            st.success(f"{new_name}님이 추가되었습니다!")
            st.rerun()
        else:
            st.error("이름을 입력해주세요.")

st.markdown("---")
st.markdown(f"<div style='text-align: center; color: gray;'>팀 일정 관리 시스템 | {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>", unsafe_allow_html=True)
