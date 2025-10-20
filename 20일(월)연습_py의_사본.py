{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyNghgGNdK8/75IGgGXM2O3O",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/mypotato20-ops/income_tax.py/blob/main/20%EC%9D%BC(%EC%9B%94)%EC%97%B0%EC%8A%B5_py%EC%9D%98_%EC%82%AC%EB%B3%B8.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": 1,
      "metadata": {
        "id": "uuCSVqlAXdVa",
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "outputId": "a48c1d07-b3bf-4d72-de55-07141f606400"
      },
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "소득 수준: 고소득층\n",
            "소득: 5,500,000원\n",
            "예상 세금: 1,100,000원\n"
          ]
        }
      ],
      "source": [
        "# 소득(income)과 세금(tax) 변수 선언\n",
        "income = 5500000  # 예시: 550만원\n",
        "tax = 0\n",
        "\n",
        "# if-else 문을 이용한 소득 수준 분류 및 세금 계산\n",
        "if income <= 1000000:\n",
        "    level = \"저소득층\"\n",
        "    tax = income * 0.05\n",
        "elif income <= 5000000:\n",
        "    level = \"중간소득층\"\n",
        "    tax = income * 0.1\n",
        "else:\n",
        "    level = \"고소득층\"\n",
        "    tax = income * 0.2\n",
        "\n",
        "# 결과 출력\n",
        "print(f\"소득 수준: {level}\")\n",
        "print(f\"소득: {income:,}원\")\n",
        "print(f\"예상 세금: {tax:,.0f}원\")"
      ]
    }
  ]
}