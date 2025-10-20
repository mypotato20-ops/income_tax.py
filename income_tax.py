# income_tax.py
income = float(input("70000000"))

if income < 2000:
    tax = income * 0.05
    level = "저소득층"
elif income < 5000:
    tax = income * 0.25
    level = "중간소득층"
else:
    tax = income * 0.50
    level = "고소득층"

print(f"\n소득 수준: {level}")
print(f"납부해야 할 세금: {tax:.2f}만원")
