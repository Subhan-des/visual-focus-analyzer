@echo off
cd /d "J:\Tool For CRO\deepgaze_tool"
call .venv\Scripts\activate
start http://localhost:8501
streamlit run app.py
pause