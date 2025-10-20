import streamlit as st

st.set_page_config(page_title="소득별 세금 계산기", page_icon="💰")

st.title("소득별 세금 계산기 💰")
st.caption("저소득 5%, 중간소득 25%, 고소득 50% 세율 적용")

# 입력
income = st.number_input(
    "당신의 소득을 입력하세요 (만원 단위):",
    min_value=0.0,
    step=100.0,
    value=0.0,
    format="%.0f"
)

# 계산 함수
def calc_tax(income: float):
    if income < 2000:
        rate = 0.05
        level = "저소득층"
    elif income < 5000:
        rate = 0.25
        level = "중간소득층"
    else:
        rate = 0.50
        level = "고소득층"
    tax = income * rate
    return level, rate, tax

# 버튼
if st.button("계산하기"):
    level, rate, tax = calc_tax(income)
    st.success(f"소득 수준: **{level}**")
    st.write(f"적용 세율: **{int(rate*100)}%**")
    st.write(f"납부해야 할 세금: **{tax:,.2f}만원**")
else:
    st.info("소득을 입력한 뒤 **계산하기** 버튼을 눌러주세요.")
