#!/usr/bin/env python3
import os
from coinbase_agentkit.wallet_providers.cdp import CdpWalletProvider
from coinbase_agentkit.action_providers.cdp import CdpActionProvider

class ExecutionAgent:
    def __init__(self, network_id="base-sepolia"):
        try:
            # AgentKit Wallet initialisieren [cite: 244-247]
            self.wallet_provider = CdpWalletProvider(
                api_key_name=os.getenv("CDP_API_KEY_NAME"),
                api_key_private_key=os.getenv("CDP_API_KEY_PRIVATE_KEY"),
                network_id=network_id 
            )
            
            # Action Provider initialisieren [cite: 248-251]
            self.action_provider = CdpActionProvider(
                wallet_provider=self.wallet_provider
            )
            self.address = self.wallet_provider.get_default_address()
            print(f"✅ Execution Agent initialisiert. Wallet-Adresse: {self.address}")
            
        except Exception as e:
            print(f"❌ FEHLER bei Initialisierung des ExecutionAgent: {e}")
            raise

    def get_balance(self):
        try:
            # Ruft die AgentKit-Funktion auf [cite: 157, 256-258]
            return self.action_provider.get_balance()
        except Exception as e:
            return {"error": str(e)}

    def execute_trade(self, from_token, to_token, amount):
        print(f"--> Führe Trade aus: {amount} {from_token} -> {to_token}")
        try:
            # Ruft die AgentKit-Funktion auf [cite: 160, 259-273]
            result = self.action_provider.trade(
                amount=amount,
                from_asset_id=from_token,
                to_asset_id=to_token
            )
            return result
        except Exception as e:
            return {"error": str(e)}

    def request_faucet(self):
        print("--> Fordere Testnet-Funds an...")
        try:
            # Ruft die AgentKit-Funktion auf [cite: 158]
            result = self.action_provider.request_faucet_funds()
            return result
        except Exception as e:
            return {"error": str(e)}
