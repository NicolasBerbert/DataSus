import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from main import get_database_connection

# Conecta ao banco de dados
conn = get_database_connection()


def render(data):
    
   st.title("📈 Análise Temporal")
   st.markdown("---")
