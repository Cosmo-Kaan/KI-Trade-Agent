#!/usr/bin/env python3
import streamlit as st
from risk_policy import RiskPolicy
from analysis_agent import AnalysisAgent
from execution_agent import ExecutionAgent

st.set_page_config(page_title="KI-Trade-Agent", layout="wide")

# --- Passwortschutz (wie bei Ihrem letzten Agenten) ---
def check_password():
    try:
        correct_password = st.secrets["APP_PASSWORD"]
    except KeyError:
        st.error("Fehler: APP_PASSWORD wurde nicht in den Streamlit Secrets gesetzt!")
        st.stop() 
    password = st.text_input("Bitte geben Sie das Passwort ein:", type="password")
    if not password: st.stop()  
    if password == correct_password: return True
    st.error("Passwort ist falsch.")
    return False

# --- Hauptanwendung ---
def run_app():
    st.title("🤖 KI-Trading Agent (AgentKit + Gemini)")
    
    # --- Netzwerk-Auswahl (WICHTIG!) ---
    st.sidebar.title("Einstellungen")
    network = st.sidebar.radio(
        "Netzwerk wählen (VORSICHT!)",
        ("base-sepolia", "base-mainnet"),
        index=0,
        help="Starten Sie IMMER mit 'base-sepolia' (Testnet). 'base-mainnet' verwendet echtes Geld!"
    )
    
    if network == "base-mainnet":
        st.error("ACHTUNG: Sie sind im Mainnet-Modus. Alle Transaktionen kosten echtes Geld!", icon="🔥")

    # --- Agenten initialisieren ---
    try:
        with st.spinner("Agenten werden initialisiert..."):
            policy = RiskPolicy(network_id=network)
            analyzer = AnalysisAgent()
            executor = ExecutionAgent(network_id=network)
    except Exception as e:
        st.error(f"Kritischer Fehler bei der Initialisierung (Prüfen Sie Ihre API-Keys): {e}")
        st.stop()

    # --- Wallet-Anzeige ---
    st.sidebar.subheader("Agenten-Wallet")
    st.sidebar.info(f"**Netzwerk:** `{network}`")
    st.sidebar.info(f"**Adresse:** `{executor.address}`")
    if st.sidebar.button("Wallet-Guthaben anzeigen"):
        st.sidebar.json(executor.get_balance())
        
    if network == "base-sepolia":
        if st.sidebar.button("Test-ETH anfordern (Faucet)"):
            st.sidebar.json(executor.request_faucet())

    # --- Das Cockpit ---
    st.subheader("Handels-Auftrag")
    query = st.text_input("Was ist die Strategie?", placeholder="z.B. Kaufe das 'DEGEN' Token")

    if st.button("Analyse & Trade ausführen", type="primary"):
        if not query:
            st.warning("Bitte geben Sie eine Strategie ein.")
            st.stop()
            
        with st.status("Autonomer Trade wird ausgeführt...", expanded=True) as status:
            # 1. ANALYSE-PHASE
            status.write("1. Analyst wird kontaktiert...")
            market_data = analyzer.search_web(query) # Daten sammeln
            status.write(f"Marktdaten gefunden: {market_data}")
            
            decision = analyzer.get_analysis(query, market_data) # Entscheidung holen
            status.write(f"Analysten-Entscheidung: {decision['reason']}")
            
            if not decision.get("trade"):
                status.error(f"Trade abgelehnt (von KI): {decision['reason']}")
                st.stop()

            # 2. RISIKO-PHASE
            trade_params = decision
            status.write("2. Risiko-Prüfung (Notbremse) wird durchgeführt...")
            is_safe, reason = policy.check_trade(
                trade_params["from_token"], 
                trade_params["to_token"], 
                trade_params["amount"]
            )
            
            if not is_safe:
                status.error(f"Trade abgelehnt (von Risiko-Policy): {reason}")
                st.stop()
            
            status.write(f"Risiko-Prüfung bestanden: {reason}")

            # 3. AUSFÜHRUNGS-PHASE
            status.write(f"3. Führe Trade aus: {trade_params['amount']} {trade_params['from_token']} -> {trade_params['to_token']}...")
            
            trade_result = executor.execute_trade(
                trade_params["from_token"], 
                trade_params["to_token"], 
                trade_params["amount"]
            )
            
            if "error" in trade_result:
                status.error(f"Trade fehlgeschlagen: {trade_result['error']}")
            else:
                status.success(f"Trade erfolgreich! Transaktions-Hash: {trade_result.get('tx_hash')}")
                st.json(trade_result)

# --- Start-Logik ---
if check_password():
    run_app()
