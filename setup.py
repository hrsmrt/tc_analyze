"""
TC Analyze - 熱帯低気圧解析ツール
"""
from setuptools import setup, find_packages

setup(
    name="tc_analyze",
    version="2.0.0",
    description="熱帯低気圧の3次元直交座標データ解析ツール",
    packages=["utils"],  # utilsパッケージのみ
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "matplotlib",
        "joblib",
    ],
)
