"""
TC Analyze - 熱帯低気圧解析ツール
"""

from setuptools import setup

setup(
    name="tc_analyze",
    version="2.0.0",
    description="熱帯低気圧の3次元直交座標データ解析ツール",
    packages=["utils", "tc_analyze", "tc_analyze.commands"],
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "joblib",
        "typer",
    ],
    entry_points={
        "console_scripts": [
            "tc-analyze=tc_analyze.cli:app",
        ],
    },
)
