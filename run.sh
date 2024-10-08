#!/bin/bash

echo -e "Executando aplicação python"
. venv/bin/activate &&  python3 -m streamlit run app/app.py
