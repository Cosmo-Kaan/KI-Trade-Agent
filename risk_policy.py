#!/usr/bin/env python3

# Definiert Ihre harten Handelsregeln
class RiskPolicy:
    def __init__(self, network_id="base-sepolia"):
        # WICHTIG: Starten Sie IMMER im Testnet!
        self.NETWORK_ID = network_id 
        
        # --- IHRE REGELN ---
        # Maximale Summe pro Trade in USDC
        self.MAX_TRADE_USD = 10.0  
        
        # Nur diese Token dürfen gehandelt werden
        self.TOKEN_WHITELIST = ["USDC", "WETH", "DEGEN"] 
        # --- ENDE IHRER REGELN ---

    def check_trade(self, from_token, to_token, amount):
        if self.NETWORK_ID == "base-mainnet" and amount > self.MAX_TRADE_USD:
            return False, f"RISIKO: Trade-Betrag ({amount} {from_token}) überschreitet max. Limit von {self.MAX_TRADE_USD} USD"
            
        if from_token not in self.TOKEN_WHITELIST or to_token not in self.TOKEN_WHITELIST:
            return False, f"RISIKO: Token ({from_token} oder {to_token}) nicht in der Whitelist."
            
        return True, "RISIKO: Prüfung bestanden."
