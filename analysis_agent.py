#!/usr/bin/env python3
import os
import json
import google.generativeai as genai
from tavily import TavilyClient

class AnalysisAgent:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.5-flash") # Oder Ihr verfügbares Modell
        self.search_tool = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    def search_web(self, query):
        try:
            response = self.search_tool.search(query=query, search_depth="basic", max_results=3)
            return [{"snippet": r["content"], "source": r["url"]} for r in response.get("results", [])]
        except Exception as e:
            return [{"error": str(e)}]

    def get_analysis(self, query, market_data):
        system_instruction = """Du bist ein Hedgefonds-Analyst. Deine einzige Aufgabe ist es, eine Handelsentscheidung in einem sauberen JSON-Format zurückzugeben.
        Analysiere die Nutzeranfrage und die Marktdaten.
        
        REGELN:
        1. Gib NUR ein JSON-Objekt zurück. KEINEN Text davor oder danach.
        2. Wenn der Trade sinnvoll ist: { "trade": true, "from_token": "USDC", "to_token": "SYMBOL", "amount": 10.0, "reason": "Kurze Begründung." }
        3. Wenn der Trade NICHT sinnvoll ist: { "trade": false, "reason": "Begründung, warum nicht." }
        4. Handle konservativ. Im Zweifelsfall: "trade": false.
        5. Der Trade-Betrag sollte immer 10.0 USDC sein.
        """
        
        user_prompt = f"""
        Nutzeranfrage: {query}
        Verfügbare Marktdaten: {json.dumps(market_data, indent=2)}
        
        Bitte gib jetzt deine JSON-Entscheidung zurück.
        """
        
        try:
            response = self.model.generate_content(user_prompt, generation_config={"response_mime_type": "application/json"})
            return json.loads(response.text)
        except Exception as e:
            return {"trade": False, "reason": f"Analyse-Fehler: {str(e)}"}
