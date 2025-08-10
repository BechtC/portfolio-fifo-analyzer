#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portfolio FIFO Analyzer
=======================
Automatische Analyse von Portfolio-CSVs mit FIFO-Prinzip
Erstellt detaillierte Reports und interaktive Visualisierungen

Unterstützte CSV-Formate:
- Semicolon (;) und Comma (,) Trennzeichen
- Verschiedene Datumsformate
- Deutsche und englische Spaltennamen
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class PortfolioFIFOAnalyzer:
    """
    Automatische FIFO-Analyse für Portfolio-CSVs
    """
    
    def __init__(self, csv_file_path, current_price=None, currency="EUR"):
        self.csv_file_path = csv_file_path
        self.current_price = current_price
        self.currency = currency
        self.company_name = ""
        self.raw_data = None
        self.transactions = None
        self.portfolio = []
        self.analysis_results = {}
        
        # Analyse ausführen
        self._load_and_clean_data()
        self._perform_fifo_analysis()
        self._calculate_summary_stats()
    
    def print_summary_report(self):
        """Detaillierter Zusammenfassungsbericht"""
        print(f"\n{'='*60}")
        print(f"🚀 {self.company_name.upper()} PORTFOLIO-ANALYSE (FIFO)")
        print(f"{'='*60}")
        
        print(f"\n💰 INVESTITIONS-ÜBERSICHT:")
        print(f"   Gesamt eingezahlt: {self.analysis_results['total_invested']:,.2f} {self.currency}")
        print(f"   Gesamt entnommen:  {self.analysis_results['total_withdrawn']:,.2f} {self.currency}")
        
        print(f"\n📈 REALISIERTE GEWINNE:")
        print(f"   Brutto-Gewinne:    {self.analysis_results['total_realized_gains']:,.2f} {self.currency}")
        print(f"   Steuern gezahlt:   {self.analysis_results['total_taxes']:,.2f} {self.currency}")
        print(f"   Netto-Gewinne:     {self.analysis_results['net_realized_gains']:,.2f} {self.currency}")
        
        print(f"\n🎯 GESAMTERGEBNIS:")
        print(f"   Gesamtgewinn:      {self.analysis_results['total_gains']:,.2f} {self.currency}")
        print(f"   Netto-Cashflow:    {self.analysis_results['net_cashflow']:,.2f} {self.currency}")
        print(f"   Gesamtrendite:     {self.analysis_results['total_return_pct']:,.1f}%")


def analyze_portfolio_from_csv(csv_file_path, current_price=None, currency="EUR"):
    """
    Hauptfunktion zur Portfolio-Analyse
    
    Args:
        csv_file_path (str): Pfad zur CSV-Datei
        current_price (float, optional): Aktueller Aktienkurs
        currency (str): Währung (Standard: EUR)
    
    Returns:
        PortfolioFIFOAnalyzer: Analyzer-Objekt mit allen Ergebnissen
    """
    analyzer = PortfolioFIFOAnalyzer(csv_file_path, current_price, currency)
    analyzer.print_summary_report()
    return analyzer


# BEISPIEL-VERWENDUNG
if __name__ == "__main__":
    print("🚀 PORTFOLIO FIFO ANALYZER")
    print("=" * 50)
    
    # HIER ANPASSEN:
    csv_file = "examples/palantir_example.csv"  # Pfad zur CSV-Datei
    current_price = 157.0  # Aktueller Kurs
    currency = "EUR"  # Währung
    
    # Analyse starten
    try:
        analyzer = analyze_portfolio_from_csv(csv_file, current_price, currency)
        
        print(f"\n✅ Analyse abgeschlossen!")
        print(f"📊 Zugriff auf Rohdaten: analyzer.analysis_results")
        
    except FileNotFoundError:
        print(f"❌ CSV-Datei nicht gefunden: {csv_file}")
        print("💡 Bitte den korrekten Pfad zur CSV-Datei angeben")
    except Exception as e:
        print(f"❌ Fehler bei der Analyse: {e}")
        print("💡 Bitte CSV-Format und Daten überprüfen")
