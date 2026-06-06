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

import sys
import io
import os
import subprocess
# Windows-Konsole auf UTF-8 umstellen (Emoji-Support)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def _open_in_chrome(filepath):
    """Öffnet eine Datei in Chrome — umgeht das leere Explorer-Fenster-Problem auf Windows."""
    abs_path = os.path.abspath(filepath)
    try:
        subprocess.Popen(['chrome.exe', abs_path])
    except FileNotFoundError:
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        for chrome in chrome_paths:
            if os.path.exists(chrome):
                subprocess.Popen([chrome, abs_path])
                return
        # Letzter Fallback
        import webbrowser
        webbrowser.open(f"file:///{abs_path}")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Deutsche Lokalisierung für Matplotlib
plt.rcParams['font.size'] = 10
plt.rcParams['figure.figsize'] = (12, 8)
sns.set_style("whitegrid")
sns.set_palette("husl")

class PortfolioFIFOAnalyzer:
    """
    Automatische FIFO-Analyse für Portfolio-CSVs
    """
    
    def __init__(self, csv_file_path, current_price=None, currency="EUR", _preloaded_df=None):
        """
        Initialisierung des Analyzers

        Args:
            csv_file_path (str): Pfad zur CSV-Datei
            current_price (float): Aktueller Kurs für Bewertung
            currency (str): Währung (EUR, USD, etc.)
            _preloaded_df (pd.DataFrame, optional): Bereits geladener und gefilterter DataFrame.
                Wenn angegeben, wird csv_file_path nicht erneut eingelesen.
        """
        self.csv_file_path = csv_file_path
        self.current_price = current_price
        self.currency = currency
        self.company_name = ""
        self.raw_data = None
        self.transactions = None
        self.portfolio = []
        self.analysis_results = {}

        # Analyse ausführen
        if _preloaded_df is not None:
            self.raw_data = _preloaded_df.copy()
            self._clean_preloaded_data()
        else:
            self._load_and_clean_data()
        self._perform_fifo_analysis()
        self._calculate_summary_stats()
    
    def _detect_delimiter(self, file_path, max_lines=5):
        """CSV-Trennzeichen automatisch erkennen"""
        with open(file_path, 'r', encoding='utf-8') as file:
            sample = []
            for i, line in enumerate(file):
                if i >= max_lines:
                    break
                sample.append(line)
        
        sample_text = '\n'.join(sample)
        
        # Häufigkeit verschiedener Trennzeichen prüfen
        delimiters = [';', ',', '\t', '|']
        delimiter_counts = {}
        
        for delimiter in delimiters:
            delimiter_counts[delimiter] = sample_text.count(delimiter)
        
        # Das häufigste Trennzeichen verwenden
        best_delimiter = max(delimiter_counts, key=delimiter_counts.get)
        print(f"🔍 Erkanntes Trennzeichen: '{best_delimiter}'")
        
        return best_delimiter
    
    def _clean_preloaded_data(self):
        """Bereinigt einen bereits geladenen DataFrame (für Multi-Asset-Modus)"""
        # Spalten normalisieren (gleiche Logik wie in _load_and_clean_data)
        column_mapping = {
            'datetime': 'datetime', 'date': 'date', 'datum': 'date',
            'price': 'price', 'preis': 'price', 'kurs': 'price',
            'shares': 'shares', 'anzahl': 'shares', 'stueck': 'shares',
            'amount': 'amount', 'betrag': 'amount', 'summe': 'amount',
            'type': 'type', 'typ': 'type', 'art': 'type',
            'tax': 'tax', 'steuer': 'tax', 'steuern': 'tax',
            'realizedgains': 'realized_gains', 'gewinn': 'realized_gains',
            'holdingname': 'company_name', 'unternehmen': 'company_name', 'name': 'company_name'
        }
        normalized_columns = {}
        for col in self.raw_data.columns:
            col_lower = col.lower().strip()
            normalized_columns[col] = column_mapping.get(col_lower, col.lower())
        self.raw_data = self.raw_data.rename(columns=normalized_columns)

        # Firmenname
        if 'company_name' in self.raw_data.columns:
            non_null = self.raw_data['company_name'].dropna()
            self.company_name = non_null.iloc[0] if len(non_null) > 0 else Path(self.csv_file_path).stem
        else:
            self.company_name = Path(self.csv_file_path).stem

        # Datentypen konvertieren
        self._convert_data_types()

        # Nach Datum sortieren
        if 'datetime' in self.raw_data.columns:
            self.raw_data['datetime'] = pd.to_datetime(self.raw_data['datetime'])
            self.transactions = self.raw_data.sort_values('datetime').reset_index(drop=True)
        elif 'date' in self.raw_data.columns:
            self.raw_data['date'] = pd.to_datetime(self.raw_data['date'], dayfirst=True)
            self.transactions = self.raw_data.sort_values('date').reset_index(drop=True)

    def _load_and_clean_data(self):
        """CSV-Daten laden und bereinigen"""
        print(f"📊 Lade CSV-Datei: {self.csv_file_path}")
        
        # Trennzeichen erkennen
        delimiter = self._detect_delimiter(self.csv_file_path)
        
        # CSV laden
        try:
            self.raw_data = pd.read_csv(self.csv_file_path, delimiter=delimiter, encoding='utf-8')
        except:
            self.raw_data = pd.read_csv(self.csv_file_path, delimiter=delimiter, encoding='latin-1')
        
        print(f"✅ CSV geladen: {len(self.raw_data)} Transaktionen")
        print(f"📋 Spalten: {list(self.raw_data.columns)}")
        
        # Spalten standardisieren
        column_mapping = {
            'datetime': 'datetime',
            'date': 'date', 
            'datum': 'date',
            'price': 'price',
            'preis': 'price',
            'kurs': 'price',
            'shares': 'shares',
            'anzahl': 'shares',
            'stueck': 'shares',
            'amount': 'amount',
            'betrag': 'amount',
            'summe': 'amount',
            'type': 'type',
            'typ': 'type',
            'art': 'type',
            'tax': 'tax',
            'steuer': 'tax',
            'steuern': 'tax',
            'realizedgains': 'realized_gains',
            'gewinn': 'realized_gains',
            'holdingname': 'company_name',
            'unternehmen': 'company_name',
            'name': 'company_name'
        }
        
        # Spaltennamen normalisieren
        normalized_columns = {}
        for col in self.raw_data.columns:
            col_lower = col.lower().strip()
            if col_lower in column_mapping:
                normalized_columns[col] = column_mapping[col_lower]
            else:
                normalized_columns[col] = col.lower()
        
        self.raw_data = self.raw_data.rename(columns=normalized_columns)
        
        # Firmenname extrahieren
        if 'company_name' in self.raw_data.columns:
            self.company_name = self.raw_data['company_name'].dropna().iloc[0]
        else:
            self.company_name = Path(self.csv_file_path).stem
        
        print(f"🏢 Unternehmen: {self.company_name}")
        
        # Datentypen konvertieren
        self._convert_data_types()
        
        # Nach Datum sortieren
        if 'datetime' in self.raw_data.columns:
            self.raw_data['datetime'] = pd.to_datetime(self.raw_data['datetime'])
            self.transactions = self.raw_data.sort_values('datetime').reset_index(drop=True)
        elif 'date' in self.raw_data.columns:
            self.raw_data['date'] = pd.to_datetime(self.raw_data['date'], dayfirst=True)
            self.transactions = self.raw_data.sort_values('date').reset_index(drop=True)
        
        print(f"✅ Daten bereinigt und sortiert")
    
    def _convert_data_types(self):
        """Datentypen konvertieren (deutsche Zahlenformate unterstützen)"""
        numeric_columns = ['price', 'shares', 'amount', 'tax', 'realized_gains']
        
        for col in numeric_columns:
            if col in self.raw_data.columns:
                # Deutsche Zahlenformate (Komma als Dezimaltrennzeichen)
                if self.raw_data[col].dtype == 'object':
                    self.raw_data[col] = self.raw_data[col].astype(str)
                    self.raw_data[col] = self.raw_data[col].str.replace(',', '.')
                    self.raw_data[col] = self.raw_data[col].str.replace(' ', '')
                
                self.raw_data[col] = pd.to_numeric(self.raw_data[col], errors='coerce').fillna(0)
    
    def _perform_fifo_analysis(self):
        """FIFO-Analyse durchführen"""
        print(f"\n🔄 Starte FIFO-Analyse...")
        
        self.portfolio = []
        self.fifo_transactions = []
        
        total_invested = 0
        total_withdrawn = 0
        total_realized_gains = 0
        total_taxes = 0
        
        for idx, transaction in self.transactions.iterrows():
            transaction_type = str(transaction.get('type', '')).lower()
            shares = transaction.get('shares', 0)
            price = transaction.get('price', 0)
            amount = transaction.get('amount', 0)
            
            if 'buy' in transaction_type or 'kauf' in transaction_type:
                # Kauf
                self.portfolio.append({
                    'date': transaction.get('date', transaction.get('datetime')),
                    'price': price,
                    'shares': shares,
                    'amount': amount
                })
                total_invested += amount
                
                self.fifo_transactions.append({
                    'date': transaction.get('date', transaction.get('datetime')),
                    'type': 'BUY',
                    'shares': shares,
                    'price': price,
                    'amount': amount,
                    'portfolio_size': sum(pos['shares'] for pos in self.portfolio),
                    'fifo_details': []
                })
                
            elif 'sell' in transaction_type or 'verkauf' in transaction_type:
                # Verkauf
                shares_to_sell = shares
                sell_details = []
                realized_gains = transaction.get('realized_gains', 0)
                taxes = transaction.get('tax', 0)
                
                while shares_to_sell > 0 and self.portfolio:
                    oldest_position = self.portfolio[0]
                    
                    if oldest_position['shares'] <= shares_to_sell:
                        # Ganze Position verkaufen
                        gain_per_share = price - oldest_position['price']
                        total_gain = gain_per_share * oldest_position['shares']
                        
                        sell_details.append({
                            'buy_date': oldest_position['date'],
                            'buy_price': oldest_position['price'],
                            'shares': oldest_position['shares'],
                            'gain_per_share': gain_per_share,
                            'total_gain': total_gain
                        })
                        
                        shares_to_sell -= oldest_position['shares']
                        self.portfolio.pop(0)
                        
                    else:
                        # Teilposition verkaufen
                        gain_per_share = price - oldest_position['price']
                        total_gain = gain_per_share * shares_to_sell
                        
                        sell_details.append({
                            'buy_date': oldest_position['date'],
                            'buy_price': oldest_position['price'],
                            'shares': shares_to_sell,
                            'gain_per_share': gain_per_share,
                            'total_gain': total_gain
                        })
                        
                        oldest_position['shares'] -= shares_to_sell
                        shares_to_sell = 0
                
                total_withdrawn += amount
                total_realized_gains += realized_gains
                total_taxes += taxes
                
                self.fifo_transactions.append({
                    'date': transaction.get('date', transaction.get('datetime')),
                    'type': 'SELL',
                    'shares': shares,
                    'price': price,
                    'amount': amount,
                    'realized_gains': realized_gains,
                    'taxes': taxes,
                    'portfolio_size': sum(pos['shares'] for pos in self.portfolio),
                    'fifo_details': sell_details
                })
        
        # Ergebnisse speichern
        self.analysis_results.update({
            'total_invested': total_invested,
            'total_withdrawn': total_withdrawn,
            'total_realized_gains': total_realized_gains,
            'total_taxes': total_taxes,
            'current_portfolio': self.portfolio.copy()
        })
        
        print(f"✅ FIFO-Analyse abgeschlossen")
    
    def _calculate_summary_stats(self):
        """Zusammenfassende Statistiken berechnen"""
        current_shares = sum(pos['shares'] for pos in self.portfolio)
        current_cost_basis = sum(pos['shares'] * pos['price'] for pos in self.portfolio)
        
        if self.current_price and current_shares > 0:
            current_value = current_shares * self.current_price
            unrealized_gains = current_value - current_cost_basis
        else:
            current_value = 0
            unrealized_gains = 0
        
        total_gains = self.analysis_results['total_realized_gains'] + unrealized_gains
        net_realized_gains = self.analysis_results['total_realized_gains'] - self.analysis_results['total_taxes']
        net_cashflow = self.analysis_results['total_withdrawn'] - self.analysis_results['total_invested'] + current_value
        
        if self.analysis_results['total_invested'] > 0:
            total_return_pct = (total_gains / self.analysis_results['total_invested']) * 100
        else:
            total_return_pct = 0
        
        self.analysis_results.update({
            'current_shares': current_shares,
            'current_cost_basis': current_cost_basis,
            'current_value': current_value,
            'unrealized_gains': unrealized_gains,
            'total_gains': total_gains,
            'net_realized_gains': net_realized_gains,
            'net_cashflow': net_cashflow,
            'total_return_pct': total_return_pct
        })
    
    def _build_reentry_data(self):
        """JSON-Daten für eingebetteten Re-Entry-Rechner aufbauen."""
        import json

        sells = []
        for tx in self.fifo_transactions:
            if tx['type'] != 'SELL':
                continue
            fifo_details = tx.get('fifo_details', [])
            avg_buy_price = 0.0
            if fifo_details:
                total_shares = sum(d['shares'] for d in fifo_details)
                avg_buy_price = (
                    sum(d['buy_price'] * d['shares'] for d in fifo_details) / total_shares
                    if total_shares > 0 else 0.0
                )
            sells.append({
                'date': str(tx.get('date', '')),
                'sellPrice': float(tx.get('price', 0)),
                'shares': float(tx.get('shares', 0)),
                'taxes': float(tx.get('taxes', 0)),
                'fee': float(tx.get('fee', 0) if tx.get('fee') else 0),
                'avgBuyPrice': round(avg_buy_price, 4),
                'fifoDetails': [
                    {
                        'buyDate': str(d.get('buy_date', '')),
                        'buyPrice': float(d.get('buy_price', 0)),
                        'shares': float(d.get('shares', 0)),
                    }
                    for d in fifo_details
                ],
            })

        portfolio = []
        for pos in self.portfolio:
            portfolio.append({
                'date': str(pos.get('date', '')),
                'buyPrice': float(pos.get('price', 0)),
                'shares': float(pos.get('shares', 0)),
            })

        data = {
            'companyName': self.company_name,
            'currentPrice': float(self.current_price) if self.current_price else None,
            'currency': self.currency,
            'sells': sells,
            'portfolio': portfolio,
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    def print_summary_report(self):
        """Detaillierter Zusammenfassungsbericht"""
        print(f"\n{'='*60}")
        print(f"🚀 {self.company_name.upper()} PORTFOLIO-ANALYSE (FIFO)")
        print(f"{'='*60}")
        
        # Investitions-Übersicht
        print(f"\n💰 INVESTITIONS-ÜBERSICHT:")
        print(f"   Gesamt eingezahlt: {self.analysis_results['total_invested']:,.2f} {self.currency}")
        print(f"   Gesamt entnommen:  {self.analysis_results['total_withdrawn']:,.2f} {self.currency}")
        
        # Realisierte Gewinne
        print(f"\n📈 REALISIERTE GEWINNE:")
        print(f"   Brutto-Gewinne:    {self.analysis_results['total_realized_gains']:,.2f} {self.currency}")
        print(f"   Steuern gezahlt:   {self.analysis_results['total_taxes']:,.2f} {self.currency}")
        print(f"   Netto-Gewinne:     {self.analysis_results['net_realized_gains']:,.2f} {self.currency}")
        
        # Aktueller Bestand
        print(f"\n📊 AKTUELLER BESTAND:")
        print(f"   Aktien:            {self.analysis_results['current_shares']:,.0f} Stück")
        print(f"   Kostenbasis:       {self.analysis_results['current_cost_basis']:,.2f} {self.currency}")
        
        if self.current_price:
            print(f"   Aktueller Wert:    {self.analysis_results['current_value']:,.2f} {self.currency} (@ {self.current_price} {self.currency})")
            print(f"   Unrealisierte Gew: {self.analysis_results['unrealized_gains']:,.2f} {self.currency}")
        
        # Gesamtergebnis
        print(f"\n🎯 GESAMTERGEBNIS:")
        print(f"   Gesamtgewinn:      {self.analysis_results['total_gains']:,.2f} {self.currency}")
        print(f"   Netto-Cashflow:    {self.analysis_results['net_cashflow']:,.2f} {self.currency}")
        print(f"   Gesamtrendite:     {self.analysis_results['total_return_pct']:,.1f}%")
        
        print(f"\n{'='*60}")

    def generate_html_report(self, output_file=None):
        """HTML-Report generieren"""
        if not output_file:
            output_file = f"output/{self.company_name.replace(' ', '_')}_portfolio_analysis.html"
        
        # Stelle sicher, dass output Verzeichnis existiert
        output_dir = Path(output_file).parent
        output_dir.mkdir(exist_ok=True)
        
        # HTML-Template erstellen
        html_content = self._create_html_template()
        
        # HTML-Datei schreiben
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML-Report erstellt: {output_file}")
        return output_file

    def _create_html_template(self):
        """Vollständiges HTML-Template erstellen"""
        # Daten für Template vorbereiten
        template_data = {
            'company_name': self.company_name,
            'current_year': datetime.now().year,
            'total_invested': f"{self.analysis_results['total_invested']:,.0f}",
            'total_withdrawn': f"{self.analysis_results['total_withdrawn']:,.0f}",
            'total_realized_gains': f"{self.analysis_results['total_realized_gains']:,.0f}",
            'total_taxes': f"{self.analysis_results['total_taxes']:,.0f}",
            'net_realized_gains': f"{self.analysis_results['net_realized_gains']:,.0f}",
            'current_shares': f"{self.analysis_results['current_shares']:,.0f}",
            'current_cost_basis': f"{self.analysis_results['current_cost_basis']:,.0f}",
            'current_value': f"{self.analysis_results['current_value']:,.0f}",
            'unrealized_gains': f"{self.analysis_results['unrealized_gains']:,.0f}",
            'total_gains': f"{self.analysis_results['total_gains']:,.0f}",
            'net_cashflow': f"{self.analysis_results['net_cashflow']:,.0f}",
            'total_return_pct': f"{self.analysis_results['total_return_pct']:,.1f}",
            'current_price': f"{self.current_price}" if self.current_price else "N/A",
            'currency': self.currency
        }
        
        reentry_json = self._build_reentry_data()

        # Hero-Section: Farben Python-seitig entscheiden
        net_realized_gains_raw = self.analysis_results['net_realized_gains']
        unrealized_gains_raw = self.analysis_results['unrealized_gains']
        total_return_pct_raw = self.analysis_results['total_return_pct']

        realized_color = 'text-emerald-400' if net_realized_gains_raw >= 0 else 'text-red-400'
        unrealized_color = 'text-emerald-400' if unrealized_gains_raw >= 0 else 'text-red-400'
        return_color = 'text-emerald-400' if total_return_pct_raw >= 0 else 'text-red-400'
        return_prefix = '+' if total_return_pct_raw >= 0 else ''
        return_display = f"{return_prefix}{total_return_pct_raw:.2f}%"

        total_invested_display = f"{self.analysis_results['total_invested']:,.2f} {self.currency}"
        total_withdrawn_display = f"{self.analysis_results['total_withdrawn']:,.2f} {self.currency}"
        net_realized_display = f"{net_realized_gains_raw:,.2f} {self.currency}"
        unrealized_display = f"{unrealized_gains_raw:,.2f} {self.currency}"

        hero_html = f"""
        <p class="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-widest mb-4">Portfolio Übersicht</p>
        <div class="grid grid-cols-2 lg:grid-cols-5 gap-4">
            <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 hover:border-indigo-500 transition-colors">
                <p class="text-gray-500 dark:text-gray-400 text-sm font-medium">Gesamt Investiert</p>
                <p class="hero-value text-3xl font-bold mt-2 text-gray-900 dark:text-gray-100">{total_invested_display}</p>
            </div>
            <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 hover:border-indigo-500 transition-colors">
                <p class="text-gray-500 dark:text-gray-400 text-sm font-medium">Gesamt Entnommen</p>
                <p class="hero-value text-3xl font-bold mt-2 text-gray-900 dark:text-gray-100">{total_withdrawn_display}</p>
            </div>
            <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 hover:border-indigo-500 transition-colors">
                <p class="text-gray-500 dark:text-gray-400 text-sm font-medium">Realisierte Gewinne</p>
                <p class="hero-value text-3xl font-bold mt-2 {realized_color}">{net_realized_display}</p>
            </div>
            <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 hover:border-indigo-500 transition-colors">
                <p class="text-gray-500 dark:text-gray-400 text-sm font-medium">Unrealisierte Gewinne</p>
                <p class="hero-value text-3xl font-bold mt-2 {unrealized_color}">{unrealized_display}</p>
            </div>
            <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 hover:border-indigo-500 transition-colors">
                <p class="text-gray-500 dark:text-gray-400 text-sm font-medium">Gesamtrendite</p>
                <p class="hero-value text-3xl font-bold mt-2 {return_color}">{return_display}</p>
            </div>
        </div>"""

        # HTML-Template (Dark Mode Skeleton)
        generation_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        html_template = f"""<!DOCTYPE html>
<html lang="de" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{template_data['company_name']} - Portfolio-Analyse {template_data['current_year']}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config = {{ darkMode: 'class' }}</script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
    <script>
        // Apply saved theme BEFORE first paint to avoid flash
        (function() {{
            var saved = localStorage.getItem('theme') || 'dark';
            if (saved === 'light') {{
                document.documentElement.classList.remove('dark');
            }} else {{
                document.documentElement.classList.add('dark');
            }}
        }})();
    </script>
</head>
<body class="bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 min-h-screen transition-colors duration-200">

    <header class="p-6 border-b border-gray-200 dark:border-gray-800">
        <div class="flex items-center justify-between">
            <div>
                <h1 id="company-name" class="text-3xl font-bold tracking-tight">{template_data['company_name'].upper()}</h1>
                <p class="text-gray-500 dark:text-gray-400 mt-1">Portfolio-Analyse · FIFO-Methode · Generiert am {generation_date}</p>
            </div>
            <div class="flex items-center gap-2">
                <button id="demo-toggle" onclick="toggleDemo()"
                    class="px-3 py-1.5 rounded-lg text-gray-400 hover:text-gray-200 border border-gray-700 hover:border-gray-500 text-sm transition-colors"
                    title="Demo-Modus: sensible Daten maskieren">
                    Demo
                </button>
                <button id="theme-toggle" onclick="toggleTheme()"
                    class="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
                    title="Dark/Light Mode wechseln">
                    <!-- Moon icon: visible in light mode (click to go dark) -->
                    <svg id="icon-moon" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 hidden" viewBox="0 0 24 24" fill="currentColor">
                        <path fill-rule="evenodd" d="M9.528 1.718a.75.75 0 01.162.819A8.97 8.97 0 009 6a9 9 0 009 9 8.97 8.97 0 003.463-.69.75.75 0 01.981.98 10.503 10.503 0 01-9.694 6.46c-5.799 0-10.5-4.701-10.5-10.5 0-4.368 2.667-8.112 6.46-9.694a.75.75 0 01.818.162z" clip-rule="evenodd" />
                    </svg>
                    <!-- Sun icon: visible in dark mode (click to go light) -->
                    <svg id="icon-sun" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.166 17.834a.75.75 0 00-1.06 1.06l1.59 1.591a.75.75 0 001.061-1.06l-1.59-1.591zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.166 6.166a.75.75 0 011.06-1.06l1.591 1.59a.75.75 0 01-1.06 1.061L6.166 6.166z" />
                    </svg>
                </button>
            </div>
        </div>
    </header>
    <script>
        function toggleTheme() {{
            var html = document.documentElement;
            var isDark = html.classList.contains('dark');
            if (isDark) {{
                html.classList.remove('dark');
                localStorage.setItem('theme', 'light');
            }} else {{
                html.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            }}
            updateThemeIcon();
        }}
        function updateThemeIcon() {{
            var isDark = document.documentElement.classList.contains('dark');
            document.getElementById('icon-sun').classList.toggle('hidden', !isDark);
            document.getElementById('icon-moon').classList.toggle('hidden', isDark);
        }}
        updateThemeIcon();

        var demoActive = false;
        var originalData = {{}};

        function toggleDemo() {{
            demoActive = !demoActive;
            var btn = document.getElementById('demo-toggle');

            if (demoActive) {{
                originalData.companyName = document.getElementById('company-name').textContent;
                originalData.heroValues = Array.from(document.querySelectorAll('.hero-value')).map(function(el) {{ return el.textContent; }});

                document.getElementById('company-name').textContent = 'DEMO CORP AG';
                document.querySelectorAll('.hero-value').forEach(function(el) {{
                    var match = el.textContent.match(/[\\d,.]+/);
                    if (match) {{
                        var num = parseFloat(match[0].replace(/\\./g, '').replace(',', '.'));
                        var fakeNum = (num * (0.5 + Math.random())).toFixed(2).replace('.', ',');
                        el.textContent = el.textContent.replace(/[\\d,.]+/, fakeNum);
                    }}
                }});

                btn.textContent = 'Demo aktiv';
                btn.classList.add('bg-orange-600', 'text-white');
                btn.classList.remove('text-gray-400');
            }} else {{
                document.getElementById('company-name').textContent = originalData.companyName;
                document.querySelectorAll('.hero-value').forEach(function(el, i) {{
                    el.textContent = originalData.heroValues[i];
                }});

                btn.textContent = 'Demo';
                btn.classList.remove('bg-orange-600', 'text-white');
                btn.classList.add('text-gray-400');
            }}
        }}
    </script>

    <main class="max-w-7xl mx-auto p-6 space-y-8">

        <div id="hero-section" class="rounded-xl border border-gray-200 dark:border-gray-800 p-6">
            {hero_html}
        </div>

        <div id="reentry-section" class="rounded-xl border border-gray-200 dark:border-gray-800 p-6">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-1">Re-Entry Rechner</h2>
            <p class="text-gray-500 dark:text-gray-400 text-sm mb-6">Berechne den optimalen Wiedereinstiegspreis nach einem Verkauf</p>

            <!-- Tabs -->
            <div class="border-b border-gray-200 dark:border-gray-800 mb-6">
                <nav class="flex gap-6">
                    <button id="reentry-tab-sells-btn" onclick="reentrySwitch('sells')"
                        class="pb-3 text-sm font-medium border-b-2 border-indigo-500 text-indigo-500 dark:text-indigo-400 transition-colors">
                        Abgeschlossene Verkäufe
                    </button>
                    <button id="reentry-tab-positions-btn" onclick="reentrySwitch('positions')"
                        class="pb-3 text-sm font-medium border-b-2 border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors">
                        Offene Positionen
                    </button>
                </nav>
            </div>

            <!-- Tab 1: Abgeschlossene Verkäufe -->
            <div id="reentry-tab-sells" class="space-y-6">
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="md:col-span-2">
                            <label class="block text-xs text-gray-400 mb-1">Verkauf auswählen</label>
                            <select id="reentry-sell-select" onchange="reentryOnSellSelect()"
                                class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-100 focus:border-indigo-500 focus:outline-none">
                                <option value="">-- Verkauf wählen --</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Verkaufserlös</label>
                            <input id="reentry-erloese" type="text" readonly
                                class="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-gray-400" />
                        </div>
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Steuer</label>
                            <input id="reentry-steuer" type="text" readonly
                                class="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-gray-400" />
                        </div>
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Nettoerlös</label>
                            <input id="reentry-netto" type="text" readonly
                                class="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-gray-400" />
                        </div>
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Ziel-Rendite %</label>
                            <input id="reentry-zielrendite" type="number" value="0" step="0.1"
                                onchange="reentryCalc()" oninput="reentryCalc()"
                                class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-100 focus:border-indigo-500 focus:outline-none" />
                        </div>
                    </div>
                    <div class="mt-6 bg-indigo-950 border border-indigo-800 rounded-xl p-4">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <p class="text-xs text-indigo-300 mb-1">Break-Even Re-Entry-Kurs</p>
                                <p id="reentry-result-kurs" class="text-2xl font-bold text-indigo-100">--</p>
                            </div>
                            <div>
                                <p class="text-xs text-indigo-300 mb-1">Nötiger Kursrückgang</p>
                                <p id="reentry-result-rueckgang" class="text-2xl font-bold text-indigo-100">--</p>
                            </div>
                        </div>
                    </div>
                    <div class="flex gap-3 mt-4">
                        <button onclick="reentryHistorySave()"
                            class="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg px-4 py-2 text-sm transition-colors">
                            In Historie speichern
                        </button>
                        <button onclick="reentryExportCSV()"
                            class="bg-gray-700 hover:bg-gray-600 text-white rounded-lg px-4 py-2 text-sm transition-colors">
                            CSV exportieren
                        </button>
                    </div>
                </div>

                <!-- Historie -->
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300">Berechnungs-Historie</h3>
                        <button onclick="reentryHistoryClear()" class="text-xs text-gray-500 hover:text-red-400 transition-colors">Löschen</button>
                    </div>
                    <div id="reentry-history-wrapper">
                        <p class="text-gray-500 text-sm">Noch keine Einträge.</p>
                    </div>
                </div>
            </div>

            <!-- Tab 2: Offene Positionen -->
            <div id="reentry-tab-positions" class="hidden space-y-6">
                <div id="reentry-lot-cards" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"></div>

                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Hypothetischer Verkaufskurs ({template_data['currency']})</label>
                            <input id="reentry-pos-vk" type="number" step="0.01" placeholder="z.B. 150.00"
                                oninput="reentryCalcTax()"
                                class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-100 focus:border-indigo-500 focus:outline-none" />
                        </div>
                        <div class="flex flex-col gap-2">
                            <label class="flex items-center gap-2 text-sm text-gray-300 mt-5 cursor-pointer">
                                <input id="reentry-kirche-cb" type="checkbox" onchange="reentryToggleKirche()"
                                    class="rounded border-gray-600 bg-gray-800 text-indigo-500 focus:ring-indigo-500" />
                                Kirchensteuer berücksichtigen
                            </label>
                            <select id="reentry-kirche-rate" disabled onchange="reentryCalcTax()"
                                class="bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-gray-400 focus:border-indigo-500 focus:outline-none disabled:cursor-not-allowed">
                                <option value="0.08">8% (Bayern, Baden-Württemberg)</option>
                                <option value="0.09">9% (übrige Bundesländer)</option>
                            </select>
                        </div>
                    </div>
                    <div class="mt-6 bg-indigo-950 border border-indigo-800 rounded-xl p-4">
                        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                            <div>
                                <p class="text-xs text-indigo-300 mb-1">Bruttogewinn</p>
                                <p id="reentry-tax-brutto" class="text-lg font-bold text-indigo-100">--</p>
                            </div>
                            <div>
                                <p class="text-xs text-indigo-300 mb-1">KapESt (25%)</p>
                                <p id="reentry-tax-kapest" class="text-lg font-bold text-indigo-100">--</p>
                            </div>
                            <div>
                                <p class="text-xs text-indigo-300 mb-1">Soli (5,5%)</p>
                                <p id="reentry-tax-soli" class="text-lg font-bold text-indigo-100">--</p>
                            </div>
                            <div id="reentry-tax-kirche-wrapper" class="hidden">
                                <p class="text-xs text-indigo-300 mb-1">Kirchensteuer</p>
                                <p id="reentry-tax-kirche" class="text-lg font-bold text-indigo-100">--</p>
                            </div>
                            <div>
                                <p class="text-xs text-indigo-300 mb-1">Nettogewinn</p>
                                <p id="reentry-tax-netto" class="text-lg font-bold text-emerald-400">--</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script>
            (function() {{
                var _selectedLot = null;
                var _currency = FIFO_DATA.currency || 'EUR';

                function fmt(n) {{
                    return isNaN(n) ? '--' : n.toLocaleString('de-DE', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
                }}

                // ── Tab switching ──────────────────────────────────────────
                window.reentrySwitch = function(tab) {{
                    var sells = document.getElementById('reentry-tab-sells');
                    var pos   = document.getElementById('reentry-tab-positions');
                    var bS    = document.getElementById('reentry-tab-sells-btn');
                    var bP    = document.getElementById('reentry-tab-positions-btn');
                    if (tab === 'sells') {{
                        sells.classList.remove('hidden'); pos.classList.add('hidden');
                        bS.className = 'pb-3 text-sm font-medium border-b-2 border-indigo-500 text-indigo-400 transition-colors';
                        bP.className = 'pb-3 text-sm font-medium border-b-2 border-transparent text-gray-400 hover:text-gray-200 transition-colors';
                    }} else {{
                        pos.classList.remove('hidden'); sells.classList.add('hidden');
                        bP.className = 'pb-3 text-sm font-medium border-b-2 border-indigo-500 text-indigo-400 transition-colors';
                        bS.className = 'pb-3 text-sm font-medium border-b-2 border-transparent text-gray-400 hover:text-gray-200 transition-colors';
                    }}
                }};

                // ── Tab 1: populate dropdown ───────────────────────────────
                var sel = document.getElementById('reentry-sell-select');
                FIFO_DATA.sells.forEach(function(s, i) {{
                    var o = document.createElement('option');
                    o.value = i;
                    o.textContent = s.date + ' — ' + fmt(s.shares) + ' Stk. à ' + fmt(s.sellPrice) + ' ' + _currency;
                    sel.appendChild(o);
                }});
                if (FIFO_DATA.sells.length === 1) {{ sel.value = '0'; reentryOnSellSelect(); }}

                window.reentryOnSellSelect = function() {{
                    var idx = sel.value;
                    if (idx === '') {{
                        document.getElementById('reentry-erloese').value = '';
                        document.getElementById('reentry-steuer').value = '';
                        document.getElementById('reentry-netto').value = '';
                        document.getElementById('reentry-result-kurs').textContent = '--';
                        document.getElementById('reentry-result-rueckgang').textContent = '--';
                        return;
                    }}
                    var s = FIFO_DATA.sells[parseInt(idx)];
                    var erloese = s.sellPrice * s.shares;
                    var netto   = erloese - s.taxes;
                    document.getElementById('reentry-erloese').value = fmt(erloese) + ' ' + _currency;
                    document.getElementById('reentry-steuer').value  = fmt(s.taxes)  + ' ' + _currency;
                    document.getElementById('reentry-netto').value   = fmt(netto)    + ' ' + _currency;
                    reentryCalc();
                }};

                window.reentryCalc = function() {{
                    var idx = sel.value;
                    if (idx === '') return;
                    var s = FIFO_DATA.sells[parseInt(idx)];
                    var erloese   = s.sellPrice * s.shares;
                    var netto     = erloese - s.taxes;
                    var ziel      = parseFloat(document.getElementById('reentry-zielrendite').value) || 0;
                    var reEntry   = (netto / s.shares) * (1 - ziel / 100);
                    var rueckgang = s.sellPrice > 0 ? (s.sellPrice - reEntry) / s.sellPrice * 100 : 0;
                    document.getElementById('reentry-result-kurs').textContent     = fmt(reEntry)   + ' ' + _currency;
                    document.getElementById('reentry-result-rueckgang').textContent = fmt(rueckgang) + ' %';
                }};

                // ── Tab 1: LocalStorage ────────────────────────────────────
                function loadHistory() {{
                    return JSON.parse(localStorage.getItem('reentry_history') || '[]');
                }}
                function renderHistory() {{
                    var hist = loadHistory();
                    var w = document.getElementById('reentry-history-wrapper');
                    if (!hist.length) {{ w.innerHTML = '<p class="text-gray-500 text-sm">Noch keine Einträge.</p>'; return; }}
                    var html = '<div class="overflow-x-auto"><table class="w-full text-sm text-left text-gray-300">';
                    html += '<thead class="text-xs text-gray-500 uppercase border-b border-gray-800"><tr>';
                    ['Datum','Aktie','Verkaufskurs','Re-Entry Kurs','Rückgang'].forEach(function(h) {{
                        html += '<th class="py-2 pr-4">' + h + '</th>';
                    }});
                    html += '</tr></thead><tbody>';
                    hist.forEach(function(e) {{
                        html += '<tr class="border-b border-gray-800/50">';
                        [e.datum, e.aktie, e.verkaufskurs, e.reEntryKurs, e.kursrueckgang_pct].forEach(function(v) {{
                            html += '<td class="py-2 pr-4">' + v + '</td>';
                        }});
                        html += '</tr>';
                    }});
                    html += '</tbody></table></div>';
                    w.innerHTML = html;
                }}
                renderHistory();

                window.reentryHistorySave = function() {{
                    var idx = sel.value;
                    if (idx === '') {{ alert('Bitte zuerst einen Verkauf auswählen.'); return; }}
                    var kursEl = document.getElementById('reentry-result-kurs');
                    if (kursEl.textContent === '--') {{ alert('Bitte zuerst berechnen.'); return; }}
                    var s = FIFO_DATA.sells[parseInt(idx)];
                    var entry = {{
                        datum: new Date().toLocaleDateString('de-DE'),
                        aktie: FIFO_DATA.companyName,
                        verkaufskurs: fmt(s.sellPrice) + ' ' + _currency,
                        reEntryKurs: kursEl.textContent,
                        kursrueckgang_pct: document.getElementById('reentry-result-rueckgang').textContent,
                    }};
                    var hist = loadHistory();
                    hist.unshift(entry);
                    localStorage.setItem('reentry_history', JSON.stringify(hist));
                    renderHistory();
                }};

                window.reentryHistoryClear = function() {{
                    if (!confirm('Alle Einträge löschen?')) return;
                    localStorage.removeItem('reentry_history');
                    renderHistory();
                }};

                window.reentryExportCSV = function() {{
                    var hist = loadHistory();
                    if (!hist.length) {{ alert('Keine Einträge in der Historie.'); return; }}
                    var csv = '﻿' + 'Datum,Aktie,Verkaufskurs,Re-Entry Kurs,Kursrueckgang\n';
                    hist.forEach(function(e) {{
                        csv += [e.datum, e.aktie, e.verkaufskurs, e.reEntryKurs, e.kursrueckgang_pct].join(',') + '\n';
                    }});
                    var blob = new Blob([csv], {{type: 'text/csv;charset=utf-8;'}});
                    var url = URL.createObjectURL(blob);
                    var a = document.createElement('a');
                    a.href = url; a.download = 'reentry_historie.csv'; a.click();
                    URL.revokeObjectURL(url);
                }};

                // ── Tab 2: Lot-Karten ──────────────────────────────────────
                var lotContainer = document.getElementById('reentry-lot-cards');
                if (!FIFO_DATA.portfolio.length) {{
                    lotContainer.innerHTML = '<p class="text-gray-500 text-sm">Keine offenen Positionen vorhanden.</p>';
                }} else {{
                    FIFO_DATA.portfolio.forEach(function(lot, i) {{
                        var card = document.createElement('div');
                        card.id = 'reentry-lot-' + i;
                        card.className = 'bg-gray-800 border border-gray-700 rounded-lg p-4 cursor-pointer hover:border-indigo-500 transition-colors';
                        card.innerHTML =
                            '<p class="text-xs text-gray-400 mb-1">Kaufdatum</p>' +
                            '<p class="text-sm font-semibold text-gray-100 mb-3">' + lot.date + '</p>' +
                            '<div class="grid grid-cols-2 gap-2">' +
                            '<div><p class="text-xs text-gray-400">Kaufkurs</p><p class="text-sm text-gray-200">' + fmt(lot.buyPrice) + ' ' + _currency + '</p></div>' +
                            '<div><p class="text-xs text-gray-400">Stückzahl</p><p class="text-sm text-gray-200">' + fmt(lot.shares) + '</p></div>' +
                            '</div>';
                        card.onclick = (function(idx) {{ return function() {{ reentrySelectLot(idx); }}; }})(i);
                        lotContainer.appendChild(card);
                    }});
                }}

                function reentrySelectLot(i) {{
                    if (_selectedLot !== null) {{
                        var prev = document.getElementById('reentry-lot-' + _selectedLot);
                        if (prev) {{ prev.className = 'bg-gray-800 border border-gray-700 rounded-lg p-4 cursor-pointer hover:border-indigo-500 transition-colors'; }}
                    }}
                    _selectedLot = i;
                    var curr = document.getElementById('reentry-lot-' + i);
                    if (curr) {{ curr.className = 'bg-indigo-950 border border-indigo-500 rounded-lg p-4 cursor-pointer transition-colors'; }}
                    reentryCalcTax();
                }}

                window.reentryToggleKirche = function() {{
                    var cb  = document.getElementById('reentry-kirche-cb');
                    var sel2 = document.getElementById('reentry-kirche-rate');
                    var wrap = document.getElementById('reentry-tax-kirche-wrapper');
                    if (cb.checked) {{
                        sel2.disabled = false;
                        sel2.className = 'bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-100 focus:border-indigo-500 focus:outline-none';
                        wrap.classList.remove('hidden');
                    }} else {{
                        sel2.disabled = true;
                        sel2.className = 'bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-gray-400 focus:border-indigo-500 focus:outline-none disabled:cursor-not-allowed';
                        wrap.classList.add('hidden');
                    }}
                    reentryCalcTax();
                }};

                window.reentryCalcTax = function() {{
                    if (_selectedLot === null) return;
                    var lot = FIFO_DATA.portfolio[_selectedLot];
                    var vk  = parseFloat(document.getElementById('reentry-pos-vk').value);
                    if (isNaN(vk)) {{
                        ['reentry-tax-brutto','reentry-tax-kapest','reentry-tax-soli','reentry-tax-kirche','reentry-tax-netto'].forEach(function(id) {{
                            document.getElementById(id).textContent = '--';
                        }});
                        return;
                    }}
                    var brutto  = (vk - lot.buyPrice) * lot.shares;
                    var kapest  = Math.max(0, brutto * 0.25);
                    var soli    = kapest * 0.055;
                    var kircheCb   = document.getElementById('reentry-kirche-cb');
                    var kircheRate = parseFloat(document.getElementById('reentry-kirche-rate').value) || 0.08;
                    var kirche  = kircheCb.checked ? kapest * kircheRate : 0;
                    var netto   = brutto - kapest - soli - kirche;
                    document.getElementById('reentry-tax-brutto').textContent = fmt(brutto)  + ' ' + _currency;
                    document.getElementById('reentry-tax-kapest').textContent = fmt(kapest)  + ' ' + _currency;
                    document.getElementById('reentry-tax-soli').textContent   = fmt(soli)    + ' ' + _currency;
                    document.getElementById('reentry-tax-kirche').textContent = fmt(kirche)  + ' ' + _currency;
                    var nettoEl = document.getElementById('reentry-tax-netto');
                    nettoEl.textContent = fmt(netto) + ' ' + _currency;
                    nettoEl.className = 'text-lg font-bold ' + (netto >= 0 ? 'text-emerald-400' : 'text-red-400');
                }};
            }})();
            </script>
        </div>

        <section id="chart-section" class="mb-8">
            <p class="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-widest mb-4">Transaktions-Timeline</p>
            <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6">
                <canvas id="transactionChart" height="120"></canvas>
            </div>
        </section>

        <section id="transactions-section" class="mb-8">
            <p class="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-widest mb-4">Transaktionen</p>

            <div class="flex gap-4 mb-4 border-b border-gray-200 dark:border-gray-800">
                <button onclick="filterTable('all')" id="tab-all" class="border-b-2 border-indigo-500 text-indigo-500 dark:text-indigo-400 pb-3 px-2 font-medium">Alle</button>
                <button onclick="filterTable('buy')" id="tab-buy" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 pb-3 px-2 transition-colors">Käufe</button>
                <button onclick="filterTable('sell')" id="tab-sell" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 pb-3 px-2 transition-colors">Verkäufe</button>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="text-gray-500 dark:text-gray-400 text-sm border-b border-gray-200 dark:border-gray-800">
                            <th class="text-left pb-3">Datum</th>
                            <th class="text-left pb-3">Typ</th>
                            <th class="text-right pb-3">Kurs (€)</th>
                            <th class="text-right pb-3">Stückzahl</th>
                            <th class="text-right pb-3">Betrag (€)</th>
                            <th class="text-right pb-3">Steuer (€)</th>
                            <th class="text-right pb-3">FIFO Kaufkurs (€)</th>
                        </tr>
                    </thead>
                    <tbody id="transactions-tbody"></tbody>
                </table>
            </div>
        </section>

    </main>

    <script>
        const FIFO_DATA = {reentry_json};

        function renderTransactions(filter) {{
            const tbody = document.getElementById('transactions-tbody');
            const allRows = [
                ...FIFO_DATA.portfolio.map(p => ({{
                    type: 'buy',
                    date: p.date,
                    price: p.buyPrice,
                    shares: p.shares,
                    amount: p.shares * p.buyPrice,
                    tax: 0,
                    fifoCost: p.buyPrice
                }})),
                ...FIFO_DATA.sells.map(s => ({{
                    type: 'sell',
                    date: s.date,
                    price: s.sellPrice,
                    shares: s.shares,
                    amount: s.shares * s.sellPrice,
                    tax: s.taxes || 0,
                    fifoCost: s.avgBuyPrice || 0
                }}))
            ].sort((a, b) => new Date(b.date) - new Date(a.date));

            const filtered = filter === 'all' ? allRows : allRows.filter(r => r.type === filter);

            tbody.innerHTML = filtered.map(r => `
                <tr class="border-b border-gray-800/50 ${{r.type === 'buy' ? 'border-l-2 border-l-emerald-500' : 'border-l-2 border-l-red-500'}} hover:bg-gray-800/30">
                    <td class="py-3 text-gray-300">${{r.date}}</td>
                    <td class="py-3"><span class="${{r.type === 'buy' ? 'text-emerald-400' : 'text-red-400'}}">${{r.type === 'buy' ? 'Kauf' : 'Verkauf'}}</span></td>
                    <td class="py-3 text-right text-gray-300">${{r.price.toFixed(2)}}</td>
                    <td class="py-3 text-right text-gray-300">${{r.shares}}</td>
                    <td class="py-3 text-right text-gray-300">${{r.amount.toFixed(2)}}</td>
                    <td class="py-3 text-right text-gray-300">${{r.tax > 0 ? r.tax.toFixed(2) : '—'}}</td>
                    <td class="py-3 text-right text-gray-300">${{r.fifoCost > 0 ? r.fifoCost.toFixed(2) : '—'}}</td>
                </tr>
            `).join('');
        }}

        function filterTable(type) {{
            ['all', 'buy', 'sell'].forEach(t => {{
                const tab = document.getElementById('tab-' + t);
                if (t === type) {{
                    tab.className = 'border-b-2 border-indigo-500 text-indigo-400 pb-3 px-2 font-medium';
                }} else {{
                    tab.className = 'text-gray-400 hover:text-gray-200 pb-3 px-2 transition-colors';
                }}
            }});
            renderTransactions(type);
        }}

        renderTransactions('all');
    </script>
    <script>
        (function() {{
            const buyData = FIFO_DATA.portfolio.map(function(p) {{
                return {{
                    x: p.date,
                    y: Math.round(p.shares * p.buyPrice * 100) / 100,
                    shares: p.shares,
                    price: p.buyPrice
                }};
            }});

            const sellData = FIFO_DATA.sells.map(function(s) {{
                return {{
                    x: s.date,
                    y: Math.round(s.shares * s.sellPrice * 100) / 100,
                    shares: s.shares,
                    price: s.sellPrice
                }};
            }});

            // Sort by date so category axis looks clean
            function dateSort(a, b) {{ return a.x < b.x ? -1 : a.x > b.x ? 1 : 0; }}
            buyData.sort(dateSort);
            sellData.sort(dateSort);

            // Collect all unique dates for a category axis
            const allDates = Array.from(new Set(
                buyData.map(function(d) {{ return d.x; }})
                .concat(sellData.map(function(d) {{ return d.x; }}))
            )).sort();

            // Remap to category index positions
            function toIndexed(dataset) {{
                return dataset.map(function(d) {{
                    return {{
                        x: allDates.indexOf(d.x),
                        y: d.y,
                        date: d.x,
                        shares: d.shares,
                        price: d.price
                    }};
                }});
            }}

            const ctx = document.getElementById('transactionChart').getContext('2d');
            new Chart(ctx, {{
                type: 'scatter',
                data: {{
                    datasets: [
                        {{
                            label: 'Käufe',
                            data: toIndexed(buyData),
                            backgroundColor: 'rgba(52, 211, 153, 0.85)',
                            borderColor: 'rgba(52, 211, 153, 1)',
                            pointRadius: 9,
                            pointHoverRadius: 12
                        }},
                        {{
                            label: 'Verkäufe',
                            data: toIndexed(sellData),
                            backgroundColor: 'rgba(248, 113, 113, 0.85)',
                            borderColor: 'rgba(248, 113, 113, 1)',
                            pointRadius: 9,
                            pointHoverRadius: 12
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#9ca3af', font: {{ size: 13 }} }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                title: function(items) {{
                                    var d = items[0].raw;
                                    return d.date || '';
                                }},
                                label: function(item) {{
                                    var d = item.raw;
                                    var currency = FIFO_DATA.currency || 'EUR';
                                    return item.dataset.label + ': ' +
                                        d.y.toLocaleString('de-DE', {{minimumFractionDigits: 2, maximumFractionDigits: 2}}) + ' ' + currency +
                                        ' (' + d.shares + ' Stk @ ' + d.price + ')';
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            type: 'linear',
                            ticks: {{
                                color: '#6b7280',
                                stepSize: 1,
                                callback: function(value) {{
                                    if (Number.isInteger(value) && value >= 0 && value < allDates.length) {{
                                        var d = allDates[value];
                                        // format YYYY-MM-DD -> DD.MM.YYYY
                                        if (d && d.length >= 10) {{
                                            return d.substring(8,10) + '.' + d.substring(5,7) + '.' + d.substring(0,4);
                                        }}
                                        return d;
                                    }}
                                    return '';
                                }}
                            }},
                            grid: {{ color: '#1f2937' }},
                            min: -0.5,
                            max: allDates.length - 0.5
                        }},
                        y: {{
                            ticks: {{
                                color: '#6b7280',
                                callback: function(v) {{
                                    return v.toLocaleString('de-DE', {{maximumFractionDigits: 0}}) + ' ' + (FIFO_DATA.currency || 'EUR');
                                }}
                            }},
                            grid: {{ color: '#1f2937' }}
                        }}
                    }}
                }}
            }});
        }})();
    </script>

</body>
</html>"""
        return html_template
    def generate_complete_report(self):
        """Vollständigen Report generieren (HTML + Console)"""
        print(f"\n🎯 VOLLSTÄNDIGER PORTFOLIO-REPORT")
        print(f"Generiert am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        
        # Kurze Konsolen-Zusammenfassung
        self.print_summary_report()
        
        # HTML-Report generieren
        print(f"\n📊 Erstelle HTML-Report...")
        html_file = self.generate_html_report()
        
        # HTML-Datei im Browser öffnen (optional)
        try:
            _open_in_chrome(html_file)
            print(f"🌐 HTML-Report im Browser geöffnet: {html_file}")
        except:
            print(f"💡 HTML-Report erstellt: {html_file}")
            print(f"   Öffne die Datei manuell im Browser für die beste Darstellung!")
        
        return html_file


def generate_multi_asset_report(analyzers_dict, output_path=None):
    """
    Generiert einen Multi-Asset HTML-Report für alle Analyzer.

    Args:
        analyzers_dict (dict): { holdingname: PortfolioFIFOAnalyzer }
        output_path (str, optional): Pfad zur Output-HTML-Datei

    Returns:
        str: Pfad zur generierten HTML-Datei
    """
    import json
    from pathlib import Path

    if not output_path:
        output_path = "output/multi_asset_portfolio_report.html"

    output_dir = Path(output_path).parent
    output_dir.mkdir(exist_ok=True)

    # ── Gesamtsummen berechnen ────────────────────────────────────────────
    total_invested = sum(a.analysis_results.get('total_invested', 0) for a in analyzers_dict.values())
    total_withdrawn = sum(a.analysis_results.get('total_withdrawn', 0) for a in analyzers_dict.values())
    total_realized_gains = sum(a.analysis_results.get('total_realized_gains', 0) for a in analyzers_dict.values())
    total_unrealized_gains = sum(a.analysis_results.get('unrealized_gains', 0) for a in analyzers_dict.values())
    total_taxes = sum(a.analysis_results.get('total_taxes', 0) for a in analyzers_dict.values())

    # ── Assets serialisieren ─────────────────────────────────────────────
    assets = {}
    for name, analyzer in analyzers_dict.items():
        reentry_raw = analyzer._build_reentry_data()
        reentry_data = json.loads(reentry_raw)

        # analysis_results: alle Werte in float/int konvertieren (Decimal, numpy, etc.)
        def _safe(v):
            try:
                return float(v)
            except (TypeError, ValueError):
                return str(v)

        ar_clean = {k: _safe(v) if not isinstance(v, (str, list, dict, type(None))) else v
                    for k, v in analyzer.analysis_results.items()
                    if k != 'current_portfolio'}  # current_portfolio ist die FIFO-Queue (list of dicts)

        assets[name] = {
            "company_name": name,
            "analysis_results": ar_clean,
            "sells": reentry_data.get("sells", []),
            "portfolio": reentry_data.get("portfolio", []),
            "has_missing_buys": False,
        }

    portfolio_data = {
        "summary": {
            "total_invested": float(total_invested),
            "total_withdrawn": float(total_withdrawn),
            "total_realized_gains": float(total_realized_gains),
            "total_unrealized_gains": float(total_unrealized_gains),
            "total_taxes": float(total_taxes),
            "asset_count": len(analyzers_dict),
        },
        "assets": assets,
    }

    portfolio_json = json.dumps(portfolio_data, ensure_ascii=False, default=str)
    generation_date = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

    html = f"""<!DOCTYPE html>
<html lang="de" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Asset Portfolio Report</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script>
        tailwind.config = {{ darkMode: 'class' }};
    </script>
    <script>
        (function() {{
            var saved = localStorage.getItem('theme');
            var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            if (saved === 'light' || (!saved && !prefersDark)) {{
                document.documentElement.classList.remove('dark');
            }} else {{
                document.documentElement.classList.add('dark');
            }}
        }})();
    </script>
</head>
<body class="bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 min-h-screen transition-colors duration-200">

    <header class="p-6 border-b border-gray-200 dark:border-gray-800">
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-3xl font-bold tracking-tight">MULTI-ASSET PORTFOLIO</h1>
                <p class="text-gray-500 dark:text-gray-400 mt-1">Portfolio-Analyse · FIFO-Methode · Generiert am {generation_date}</p>
            </div>
            <div class="flex items-center gap-2">
                <button id="demo-toggle" onclick="toggleDemo()"
                    class="px-3 py-1.5 rounded-lg text-xs font-medium bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-200 dark:hover:bg-indigo-800 transition-colors"
                    title="Demo-Modus: Namen und Zahlen maskieren">
                    Demo
                </button>
                <button id="theme-toggle" onclick="toggleTheme()"
                    class="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
                    title="Dark/Light Mode wechseln">
                    <svg id="icon-moon" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 hidden" viewBox="0 0 24 24" fill="currentColor">
                        <path fill-rule="evenodd" d="M9.528 1.718a.75.75 0 01.162.819A8.97 8.97 0 009 6a9 9 0 009 9 8.97 8.97 0 003.463-.69.75.75 0 01.981.98 10.503 10.503 0 01-9.694 6.46c-5.799 0-10.5-4.701-10.5-10.5 0-4.368 2.667-8.112 6.46-9.694a.75.75 0 01.818.162z" clip-rule="evenodd" />
                    </svg>
                    <svg id="icon-sun" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.166 17.834a.75.75 0 00-1.06 1.06l1.59 1.591a.75.75 0 001.061-1.06l-1.59-1.591zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.166 6.166a.75.75 0 011.06-1.06l1.591 1.59a.75.75 0 01-1.06 1.061L6.166 6.166z" />
                    </svg>
                </button>
            </div>
        </div>
    </header>

    <script>
        function toggleTheme() {{
            var html = document.documentElement;
            var isDark = html.classList.contains('dark');
            if (isDark) {{
                html.classList.remove('dark');
                localStorage.setItem('theme', 'light');
            }} else {{
                html.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            }}
            updateThemeIcon();
        }}
        function updateThemeIcon() {{
            var isDark = document.documentElement.classList.contains('dark');
            document.getElementById('icon-sun').classList.toggle('hidden', !isDark);
            document.getElementById('icon-moon').classList.toggle('hidden', isDark);
        }}
        updateThemeIcon();
    </script>

    <main class="max-w-7xl mx-auto p-6 space-y-8">
        <div id="portfolio-view">
            <!-- Summary-Kennzahlen -->
            <div id="summary-bar" class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-4">
                    <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Gesamt Investiert</p>
                    <p id="sum-invested" class="text-2xl font-bold"></p>
                </div>
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-4">
                    <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Gesamt Realisiert</p>
                    <p id="sum-realized" class="text-2xl font-bold"></p>
                </div>
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-4">
                    <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Gesamt Unrealisiert</p>
                    <p id="sum-unrealized" class="text-2xl font-bold"></p>
                </div>
            </div>
            <!-- Filter & Sortierung -->
            <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
                <div class="flex items-center gap-1 border-b border-gray-200 dark:border-gray-700">
                    <button id="filter-all" onclick="setFilter('all')" class="border-b-2 border-indigo-500 text-indigo-400 pb-2 px-3 font-medium text-sm">Alle</button>
                    <button id="filter-open" onclick="setFilter('open')" class="text-gray-400 hover:text-gray-200 pb-2 px-3 text-sm transition-colors">Offen</button>
                    <button id="filter-closed" onclick="setFilter('closed')" class="text-gray-400 hover:text-gray-200 pb-2 px-3 text-sm transition-colors">Geschlossen</button>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-xs text-gray-500 dark:text-gray-400">Sortierung:</span>
                    <button id="sort-return" onclick="setSort('return')" class="bg-indigo-600 text-white px-3 py-1.5 rounded-lg text-sm font-medium">Rendite %</button>
                    <button id="sort-name" onclick="setSort('name')" class="bg-gray-800 dark:bg-gray-800 text-gray-400 hover:text-gray-200 px-3 py-1.5 rounded-lg text-sm transition-colors">Name</button>
                    <button id="sort-invested" onclick="setSort('invested')" class="bg-gray-800 dark:bg-gray-800 text-gray-400 hover:text-gray-200 px-3 py-1.5 rounded-lg text-sm transition-colors">Investiert</button>
                </div>
            </div>
            <!-- Karten-Grid -->
            <div id="assets-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"></div>
        </div>
        <div id="detail-view" style="display:none" class="p-6">
          <button onclick="showOverview()" class="mb-6 flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm">
            ← Zurück zur Übersicht
          </button>
          <h2 id="detail-title" class="text-2xl font-bold mb-6"></h2>
          <div id="detail-hero" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-4"></div>

          <!-- Aktueller Kurs -->
          <div id="detail-live-price-box" class="hidden flex items-center gap-3 mb-6 bg-gray-900 border border-indigo-800 rounded-xl px-4 py-3">
            <span class="text-xs text-indigo-400 font-medium whitespace-nowrap">Aktueller Kurs (manuell):</span>
            <input id="detail-live-price" type="number" step="0.01" placeholder="z.B. 112.50"
              oninput="applyLivePrice()"
              class="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white w-36 focus:border-indigo-500 focus:outline-none">
            <span class="text-xs text-gray-500">€ · Unrealisiert &amp; Rendite werden sofort aktualisiert</span>
          </div>

          <!-- Chart -->
          <div class="bg-gray-900 rounded-xl p-4 border border-gray-800 mb-6">
            <h3 class="text-sm font-medium text-gray-400 uppercase tracking-wide mb-1">Kauf- & Verkaufshistorie</h3>
            <p class="text-xs text-gray-500 mb-3">Oben: Kurs (€) · Unten: Stückzahl pro Transaktion</p>
            <canvas id="detail-chart" height="100"></canvas>
            <div class="mt-3 border-t border-gray-800 pt-3">
              <canvas id="detail-chart-volume" height="60"></canvas>
            </div>
          </div>

          <!-- Transaktions-Tabelle -->
          <div class="bg-gray-900 rounded-xl p-4 border border-gray-800">
            <h3 class="text-sm font-medium text-gray-400 uppercase tracking-wide mb-4">Transaktionen (chronologisch)</h3>
            <div class="overflow-x-auto">
              <table class="w-full text-xs">
                <thead>
                  <tr class="text-gray-400 border-b border-gray-800">
                    <th class="text-left py-2 pr-3">Datum</th>
                    <th class="text-left py-2 pr-3">Typ</th>
                    <th class="text-right py-2 pr-3">Kurs</th>
                    <th class="text-right py-2 pr-3">Stück</th>
                    <th class="text-right py-2 pr-3">Betrag</th>
                    <th class="text-right py-2 pr-3">Gewinn/Verlust</th>
                    <th class="text-right py-2">Steuer</th>
                  </tr>
                </thead>
                <tbody id="tx-body"></tbody>
              </table>
            </div>
          </div>

          <!-- Re-Entry Rechner -->
          <div class="bg-gray-900 rounded-xl p-4 border border-gray-800 mt-6">
            <h3 class="text-sm font-medium text-gray-400 uppercase tracking-wide mb-1">Re-Entry Rechner</h3>

            <!-- Kirchensteuer (geteilt zwischen beiden Modi) -->
            <div class="flex items-center gap-3 mb-4">
              <label class="text-xs text-gray-400">Kirchensteuer:</label>
              <select id="reentry-kirche" onchange="reentryCalc(); simUpdate();" class="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white">
                <option value="0">Keine</option>
                <option value="0.08">8 % (Bayern / BW)</option>
                <option value="0.09">9 % (übrige Bundesländer)</option>
              </select>
            </div>

            <!-- Moduswahl-Tabs -->
            <div class="flex gap-2 mb-4 border-b border-gray-700 pb-0">
              <button id="reentry-tab-historic" onclick="reentrySetMode('historic')"
                class="text-xs px-4 py-2 rounded-t-lg font-medium transition-colors bg-indigo-600 text-white">
                Historischer Verkauf
              </button>
              <button id="reentry-tab-simulate" onclick="reentrySetMode('simulate')"
                class="text-xs px-4 py-2 rounded-t-lg font-medium transition-colors bg-gray-800 text-gray-400 hover:text-white">
                Verkauf simulieren
              </button>
            </div>

            <!-- Panel: Historischer Verkauf -->
            <div id="reentry-historic-panel">
              <p class="text-xs text-gray-500 mb-4">Wähle einen Verkauf und berechne, ab welchem Kurs sich ein Rückkauf lohnt.</p>
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
                <div class="sm:col-span-2 lg:col-span-3">
                  <label class="text-xs text-gray-400 block mb-1">Verkauf auswählen (oder manuell eingeben)</label>
                  <select id="reentry-sell-select" onchange="reentryOnSelectChange()" class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white"></select>
                </div>
                <div>
                  <label class="text-xs text-gray-400 block mb-1">Verkaufskurs (€)</label>
                  <input id="reentry-sell-price" type="number" step="0.01" oninput="reentryCalc()" class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white">
                </div>
                <div>
                  <label class="text-xs text-gray-400 block mb-1">Stückzahl</label>
                  <input id="reentry-shares" type="number" step="0.0001" oninput="reentryCalc()" class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white">
                </div>
                <div>
                  <label class="text-xs text-gray-400 block mb-1">Gezahlte Steuer (€)</label>
                  <input id="reentry-tax" type="number" step="0.01" oninput="reentryCalc()" class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white">
                </div>
                <div>
                  <label class="text-xs text-gray-400 block mb-1">Erwartete Gebühren Rückkauf (€)</label>
                  <input id="reentry-fee" type="number" step="0.01" value="0" oninput="reentryCalc()" class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white">
                </div>
                <div>
                  <label class="text-xs text-gray-400 block mb-1">Ziel-Gewinn über Break-Even (€)</label>
                  <input id="reentry-extra" type="number" step="0.01" value="0" oninput="reentryCalc()" class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white">
                </div>
              </div>

              <!-- Steuer-Schnellrechner -->
              <div class="flex items-center gap-2 mb-4">
                <button onclick="reentryAutoTax()" class="text-xs bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg px-3 py-1.5 text-indigo-400 transition-colors">
                  Steuer automatisch berechnen (aus Gewinn)
                </button>
                <span class="text-xs text-gray-500">Abgeltung 25 % + Soli 5,5 % (+ optional Kirchensteuer)</span>
              </div>
            </div>

            <!-- Panel: Verkauf simulieren -->
            <div id="reentry-simulate-panel" class="hidden">
              <p class="text-xs text-gray-500 mb-4">Simuliere einen Verkauf deiner offenen Positionen zu einem Zielkurs.</p>
              <div id="reentry-simulate-no-positions" class="hidden text-xs text-gray-500 italic mb-4">Keine offenen Positionen vorhanden.</div>
              <div id="reentry-simulate-inputs">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-3">
                  <div>
                    <label class="text-xs text-gray-400 block mb-1">Zielkurs (€)</label>
                    <input id="sim-target-price" type="number" step="0.01" placeholder="z.B. 95.00" oninput="simUpdate()" class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white">
                  </div>
                  <div>
                    <label class="text-xs text-gray-400 block mb-1">Stückzahl</label>
                    <div class="flex gap-2">
                      <input id="sim-shares" type="number" step="0.0001" placeholder="z.B. 50" oninput="simUpdate()" class="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white">
                      <button id="sim-all-btn" onclick="simSetAll()" class="text-xs bg-gray-700 hover:bg-gray-600 border border-gray-600 rounded-lg px-3 py-2 text-gray-300 whitespace-nowrap transition-colors"></button>
                    </div>
                  </div>
                </div>
                <div id="sim-remaining" class="text-xs text-gray-400 mb-4 hidden">
                  Verbleibend nach Verkauf: <span id="sim-remaining-val" class="text-white font-medium"></span>
                </div>
                <div id="sim-warn-overstock" class="hidden text-xs text-amber-400 mb-3">⚠ Mehr Stücke als im Bestand eingegeben.</div>
                <!-- Platzhalter für FIFO-Vorschau-Tabelle (#29) -->
                <div id="reentry-simulate-lots"></div>
              </div>
            </div>

            <div id="reentry-result" class="hidden bg-gray-800 rounded-lg p-4 border border-gray-700 mb-4">
              <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 text-xs mb-3">
                <div>
                  <p class="text-gray-400 mb-1">Netto-Erlös</p>
                  <p id="reentry-net" class="font-bold text-white text-base"></p>
                </div>
                <div>
                  <p class="text-gray-400 mb-1">Break-Even Kurs</p>
                  <p id="reentry-breakeven" class="font-bold text-indigo-400 text-base"></p>
                </div>
                <div>
                  <p class="text-gray-400 mb-1">Muss sinken um</p>
                  <p id="reentry-drop-pct" class="font-bold text-amber-400 text-base"></p>
                </div>
                <div>
                  <p class="text-gray-400 mb-1">Ziel-Kurs</p>
                  <p id="reentry-target" class="font-bold text-emerald-400 text-base"></p>
                </div>
                <div>
                  <p class="text-gray-400 mb-1">Ziel-Gewinn</p>
                  <p id="reentry-gain" class="font-bold text-emerald-400 text-base"></p>
                </div>
              </div>
              <p class="text-xs text-gray-400" id="reentry-hint"></p>
            </div>

            <!-- Notiz speichern -->
            <div class="border-t border-gray-800 pt-4 mt-2">
              <label class="text-xs text-gray-400 block mb-1">Notiz / Begründung speichern</label>
              <textarea id="reentry-note" rows="2" placeholder="z.B. Warte auf Rücksetzer auf 90 €, dann Wiedereinstieg mit 50 Stk..." class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white resize-none mb-2"></textarea>
              <button onclick="reentrySave()" class="text-xs bg-indigo-600 hover:bg-indigo-700 rounded-lg px-4 py-2 text-white font-medium transition-colors">Speichern</button>
            </div>

            <!-- FIFO-Chargen bei historischem Verkauf -->
            <div id="reentry-fifo-details" class="hidden"></div>

            <!-- Gespeicherte Analysen -->
            <div id="reentry-saved-area" class="mt-4 hidden">
              <p class="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">Gespeicherte Analysen</p>
              <div id="reentry-saved-list" class="space-y-2"></div>
            </div>
          </div>

        </div>
    </main>

    <script>
        const PORTFOLIO_DATA = {portfolio_json};
        console.log('PORTFOLIO_DATA geladen:', Object.keys(PORTFOLIO_DATA.assets).length, 'Aktien');

        // ── Demo-Modus ──────────────────────────────────────────────────
        var _demoActive = false;
        var _origData = null;

        function _randomAmount(base) {{
            return (Math.random() * 50000 + 1000).toFixed(2);
        }}

        function toggleDemo() {{
            _demoActive = !_demoActive;
            var btn = document.getElementById('demo-toggle');
            btn.classList.toggle('bg-indigo-300', _demoActive);
            btn.classList.toggle('dark:bg-indigo-700', _demoActive);
            renderOverview();
            renderSummary();
        }}

        // ── Formatierung ─────────────────────────────────────────────────
        function fmt(val, decimals) {{
            if (val === null || val === undefined || isNaN(val)) return '—';
            return Number(val).toLocaleString('de-DE', {{
                minimumFractionDigits: decimals ?? 2,
                maximumFractionDigits: decimals ?? 2
            }});
        }}

        function fmtEur(val) {{
            if (_demoActive) val = parseFloat(_randomAmount());
            return fmt(val) + ' €';
        }}

        function fmtShares(val) {{
            var n = parseFloat(val);
            if (isNaN(n)) return '—';
            // Ganze Zahlen ohne Dezimalstellen, sonst max. 4 signifikante Nachkommastellen
            if (n === Math.floor(n)) return n.toLocaleString('de-DE');
            return n.toLocaleString('de-DE', {{ minimumFractionDigits: 0, maximumFractionDigits: 4 }});
        }}

        function fmtPct(val) {{
            if (val === null || val === undefined || isNaN(val)) return '—';
            if (_demoActive) val = (Math.random() * 200 - 100);
            return (val >= 0 ? '+' : '') + fmt(val) + ' %';
        }}

        // ── Summary-Bar ──────────────────────────────────────────────────
        function renderSummary() {{
            var s = PORTFOLIO_DATA.summary;
            document.getElementById('sum-invested').textContent   = fmtEur(s.total_invested);
            document.getElementById('sum-realized').textContent   = fmtEur(s.total_realized_gains);
            document.getElementById('sum-unrealized').textContent = fmtEur(s.total_unrealized_gains);
        }}

        // ── Filter & Sort State ──────────────────────────────────────────
        var currentFilter = 'all';
        var currentSort = 'return';

        function filterAndSort() {{
            var assets = Object.entries(PORTFOLIO_DATA.assets);

            // Filter
            if (currentFilter === 'open') {{
                assets = assets.filter(function(e) {{ return e[1].portfolio && e[1].portfolio.length > 0; }});
            }} else if (currentFilter === 'closed') {{
                assets = assets.filter(function(e) {{ return !e[1].portfolio || e[1].portfolio.length === 0; }});
            }}

            // Sort
            if (currentSort === 'return') {{
                assets.sort(function(a, b) {{ return (b[1].analysis_results.total_return_pct || 0) - (a[1].analysis_results.total_return_pct || 0); }});
            }} else if (currentSort === 'name') {{
                assets.sort(function(a, b) {{ return a[0].localeCompare(b[0]); }});
            }} else if (currentSort === 'invested') {{
                assets.sort(function(a, b) {{ return (b[1].analysis_results.total_invested || 0) - (a[1].analysis_results.total_invested || 0); }});
            }}

            renderGrid(assets);
        }}

        function setFilter(f) {{
            currentFilter = f;
            ['all', 'open', 'closed'].forEach(function(id) {{
                var el = document.getElementById('filter-' + id);
                el.className = f === id
                    ? 'border-b-2 border-indigo-500 text-indigo-400 pb-2 px-3 font-medium text-sm'
                    : 'text-gray-400 hover:text-gray-200 pb-2 px-3 text-sm transition-colors';
            }});
            filterAndSort();
        }}

        function setSort(s) {{
            currentSort = s;
            ['return', 'name', 'invested'].forEach(function(id) {{
                var el = document.getElementById('sort-' + id);
                el.className = s === id
                    ? 'bg-indigo-600 text-white px-3 py-1.5 rounded-lg text-sm font-medium'
                    : 'bg-gray-800 dark:bg-gray-800 text-gray-400 hover:text-gray-200 px-3 py-1.5 rounded-lg text-sm transition-colors';
            }});
            filterAndSort();
        }}

        // ── Karten-Grid ──────────────────────────────────────────────────
        function renderGrid(assets) {{
            var grid = document.getElementById('assets-grid');
            grid.innerHTML = '';
            assets.forEach(function(entry) {{
                var name = entry[0];
                var asset = entry[1];
                var r = asset.analysis_results;
                var ret = _demoActive ? (Math.random() * 200 - 100) : r.total_return_pct;
                var isPositive = ret >= 0;
                var borderClass = isPositive ? 'border-l-4 border-emerald-500' : 'border-l-4 border-red-500';
                var retColorClass = isPositive ? 'text-emerald-500' : 'text-red-500';
                var retText = (ret !== null && ret !== undefined && !isNaN(ret))
                    ? (ret >= 0 ? '+' : '') + fmt(ret) + ' %'
                    : '—';
                var displayName = _demoActive ? 'Demo Corp AG' : name;
                var missingBadge = asset.has_missing_buys
                    ? '<span class="ml-2 px-1.5 py-0.5 text-xs rounded bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300 font-medium">&#9888; Unvollständig</span>'
                    : '';
                var card = document.createElement('div');
                card.className = 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 ' + borderClass + ' rounded-xl p-4 cursor-pointer hover:shadow-md hover:border-gray-300 dark:hover:border-gray-600 transition-all';
                card.addEventListener('click', (function(n) {{ return function() {{ showDetail(n); }}; }})(name));
                card.innerHTML = '<div class="flex items-start justify-between mb-2">'
                    + '<p class="font-semibold truncate flex-1 mr-2" title="' + displayName + '">' + displayName + '</p>'
                    + missingBadge
                    + '</div>'
                    + '<p class="text-2xl font-bold ' + retColorClass + ' mb-3">' + retText + '</p>'
                    + '<div class="grid grid-cols-2 gap-x-3 gap-y-1 text-xs">'
                    + '<span class="text-gray-500 dark:text-gray-400">Investiert</span>'
                    + '<span class="text-right font-medium">' + fmtEur(r.total_invested) + '</span>'
                    + '<span class="text-gray-500 dark:text-gray-400">Entnommen</span>'
                    + '<span class="text-right font-medium">' + fmtEur(r.total_withdrawn) + '</span>'
                    + '<span class="text-gray-500 dark:text-gray-400">Realisiert</span>'
                    + '<span class="text-right font-medium">' + fmtEur(r.total_realized_gains) + '</span>'
                    + '<span class="text-gray-500 dark:text-gray-400">Unrealisiert</span>'
                    + '<span class="text-right font-medium">' + fmtEur(r.unrealized_gains) + '</span>'
                    + '</div>';
                grid.appendChild(card);
            }});
        }}

        function renderOverview() {{
            filterAndSort();
        }}

        function showDetail(assetName) {{
            document.getElementById('portfolio-view').style.display = 'none';
            document.getElementById('detail-view').style.display = 'block';

            var asset = PORTFOLIO_DATA.assets[assetName];
            var r = asset.analysis_results;

            document.getElementById('detail-title').textContent = assetName;

            var currentShares = (asset.portfolio || []).reduce(function(s, p) {{ return s + (parseFloat(p.shares) || 0); }}, 0);
            var costBasis = (asset.portfolio || []).reduce(function(s, p) {{ return s + (parseFloat(p.buyPrice) || 0) * (parseFloat(p.shares) || 0); }}, 0);
            window._detailShares = currentShares;
            window._detailCostBasis = costBasis;
            renderDetailHero(r, currentShares, costBasis, null);

            // Chart + Tabelle aufbauen
            renderDetailChart(asset);
            window._currentAsset = asset;
            renderTxTable();
            reentryPopulateSells(asset.sells || []);
        }}

        function renderDetailHero(r, currentShares, costBasis, livePrice) {{
            var unrealized = (livePrice != null && currentShares > 0)
                ? (livePrice * currentShares) - costBasis
                : r.unrealized_gains;
            var totalGains = (parseFloat(r.total_realized_gains) || 0) + unrealized;
            var totalReturn = costBasis > 0 && livePrice != null
                ? ((livePrice * currentShares - costBasis) / (parseFloat(r.total_invested) || 1)) * 100
                : r.total_return_pct;

            var metrics = [
                {{ label: 'Investiert',   value: fmtEur(r.total_invested) }},
                {{ label: 'Entnommen',    value: fmtEur(r.total_withdrawn) }},
                {{ label: 'Realisiert',   value: fmtEur(r.total_realized_gains) }},
                {{ label: 'Unrealisiert', value: fmtEur(unrealized), isReturn: true, val: unrealized }},
                {{ label: 'Rendite',      value: fmtPct(totalReturn), isReturn: true, val: totalReturn }},
                {{ label: 'Im Bestand',   value: currentShares > 0 ? fmtShares(currentShares) + ' Stk' : '— (geschlossen)', isStock: true, val: currentShares }},
            ];

            var hero = document.getElementById('detail-hero');
            hero.innerHTML = '';
            metrics.forEach(function(m) {{
                var colorClass = m.isReturn
                    ? (m.val >= 0 ? 'text-emerald-400' : 'text-red-400')
                    : m.isStock
                        ? (m.val > 0 ? 'text-indigo-400' : 'text-gray-500')
                    : 'text-white';
                var card = document.createElement('div');
                card.className = 'bg-gray-900 rounded-xl p-4 border border-gray-800';
                card.innerHTML = '<p class="text-xs text-gray-400 uppercase tracking-wide mb-1">' + m.label + '</p>'
                    + '<p class="text-xl font-bold ' + colorClass + '">' + m.value + '</p>';
                hero.appendChild(card);
            }});

            // Kurs-Eingabefeld unter dem Hero
            var liveBox = document.getElementById('detail-live-price-box');
            if (currentShares > 0) {{
                liveBox.classList.remove('hidden');
                var inp = document.getElementById('detail-live-price');
                if (livePrice != null) inp.value = livePrice;
            }} else {{
                liveBox.classList.add('hidden');
            }}
        }}

        function applyLivePrice() {{
            var val = parseFloat(document.getElementById('detail-live-price').value);
            var r = window._currentAsset ? window._currentAsset.analysis_results : null;
            if (!r) return;
            renderDetailHero(r, window._detailShares, window._detailCostBasis, isNaN(val) ? null : val);
        }}

        var _detailChart = null;
        var _detailChartVolume = null;

        function renderDetailChart(asset) {{
            if (_detailChart) {{ _detailChart.destroy(); _detailChart = null; }}
            if (_detailChartVolume) {{ _detailChartVolume.destroy(); _detailChartVolume = null; }}

            // ── Daten aufbereiten ────────────────────────────────────────
            function parseDateLabel(d) {{
                if (!d) return '';
                if (d.indexOf('.') !== -1) {{
                    var p = d.split('.');
                    return p[2] + '-' + p[1] + '-' + p[0];
                }}
                return d.substring(0, 10);
            }}

            // Alle Ereignisse sammeln und nach Datum sortieren
            var events = [];
            (asset.portfolio || []).forEach(function(p) {{
                events.push({{ date: parseDateLabel(p.date), price: parseFloat(p.buyPrice) || 0, shares: parseFloat(p.shares) || 0, type: 'buy' }});
            }});
            (asset.sells || []).forEach(function(s) {{
                events.push({{ date: parseDateLabel(s.date), price: parseFloat(s.sellPrice) || 0, shares: parseFloat(s.shares) || 0, type: 'sell' }});
                // Kaufchargen ebenfalls
                (s.fifoDetails || []).forEach(function(fd) {{
                    events.push({{ date: parseDateLabel(fd.buyDate), price: parseFloat(fd.buyPrice) || 0, shares: parseFloat(fd.shares) || 0, type: 'buy' }});
                }});
            }});
            events.sort(function(a, b) {{ return a.date.localeCompare(b.date); }});

            // Duplikate (gleicher Tag + Typ) zusammenfassen
            var byDay = {{}};
            events.forEach(function(e) {{
                var key = e.date + '|' + e.type;
                if (!byDay[key]) byDay[key] = {{ date: e.date, type: e.type, totalShares: 0, prices: [] }};
                byDay[key].totalShares += e.shares;
                byDay[key].prices.push(e.price);
            }});
            var days = Object.values(byDay).sort(function(a, b) {{ return a.date.localeCompare(b.date); }});
            var allDates = [...new Set(days.map(function(d) {{ return d.date; }}))].sort();

            // Scatter-Punkte: Durchschnittskurs pro Tag+Typ
            var buyPoints  = days.filter(function(d) {{ return d.type === 'buy'; }}).map(function(d) {{
                var avg = d.prices.reduce(function(s, v) {{ return s + v; }}, 0) / d.prices.length;
                return {{ x: d.date, y: avg, shares: d.totalShares }};
            }});
            var sellPoints = days.filter(function(d) {{ return d.type === 'sell'; }}).map(function(d) {{
                var avg = d.prices.reduce(function(s, v) {{ return s + v; }}, 0) / d.prices.length;
                return {{ x: d.date, y: avg, shares: d.totalShares }};
            }});

            // ── Chart 1: Kurs-Scatter ────────────────────────────────────
            var ctx1 = document.getElementById('detail-chart').getContext('2d');
            _detailChart = new Chart(ctx1, {{
                type: 'scatter',
                data: {{
                    datasets: [
                        {{ label: 'Käufe',    data: buyPoints,  backgroundColor: 'rgba(52,211,153,0.85)', pointRadius: 7 }},
                        {{ label: 'Verkäufe', data: sellPoints, backgroundColor: 'rgba(248,113,113,0.85)', pointRadius: 7 }}
                    ]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{ labels: {{ color: '#9ca3af' }} }},
                        tooltip: {{ callbacks: {{ label: function(c) {{
                            return c.dataset.label + ': ' + c.parsed.y.toFixed(2) + ' € · ' + c.raw.shares + ' Stk';
                        }} }} }}
                    }},
                    scales: {{
                        x: {{ type: 'category', labels: allDates, ticks: {{ color: '#6b7280', maxRotation: 45 }}, grid: {{ color: '#1f2937' }} }},
                        y: {{ ticks: {{ color: '#6b7280', callback: function(v) {{ return v + ' €'; }} }}, grid: {{ color: '#1f2937' }} }}
                    }}
                }}
            }});

            // ── Chart 2: Stückzahl-Balken ────────────────────────────────
            var buyBars  = allDates.map(function(d) {{
                var e = days.find(function(x) {{ return x.date === d && x.type === 'buy'; }});
                return e ? e.totalShares : 0;
            }});
            var sellBars = allDates.map(function(d) {{
                var e = days.find(function(x) {{ return x.date === d && x.type === 'sell'; }});
                return e ? -e.totalShares : 0;  // negativ = nach unten
            }});

            var ctx2 = document.getElementById('detail-chart-volume').getContext('2d');
            _detailChartVolume = new Chart(ctx2, {{
                type: 'bar',
                data: {{
                    labels: allDates,
                    datasets: [
                        {{ label: 'Gekauft',  data: buyBars,  backgroundColor: 'rgba(52,211,153,0.7)',  borderRadius: 3 }},
                        {{ label: 'Verkauft', data: sellBars, backgroundColor: 'rgba(248,113,113,0.7)', borderRadius: 3 }}
                    ]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{ labels: {{ color: '#9ca3af', boxWidth: 12 }} }},
                        tooltip: {{ callbacks: {{ label: function(c) {{
                            return c.dataset.label + ': ' + Math.abs(c.parsed.y) + ' Stk';
                        }} }} }}
                    }},
                    scales: {{
                        x: {{ ticks: {{ color: '#6b7280', maxRotation: 45 }}, grid: {{ color: '#1f2937' }} }},
                        y: {{ ticks: {{ color: '#6b7280', callback: function(v) {{ return Math.abs(v) + ' Stk'; }} }}, grid: {{ color: '#1f2937' }} }}
                    }}
                }}
            }});
        }}

        function setTxTab(tab) {{}}  // wird nicht mehr genutzt, bleibt für Kompatibilität

        function renderTxTable() {{
            var asset = window._currentAsset;
            if (!asset) return;
            var body = document.getElementById('tx-body');
            body.innerHTML = '';

            // ── Verkäufe (chronologisch) mit FIFO-Sub-Zeilen ──────────────
            function dateToSortKey(d) {{
                if (!d) return '';
                // Unterstützt dd.mm.yyyy und yyyy-mm-dd
                if (d.indexOf('.') !== -1) {{
                    var p = d.split('.');
                    return p[2] + '-' + p[1] + '-' + p[0];
                }}
                return d.substring(0, 10);
            }}

            var sells = (asset.sells || []).slice().sort(function(a, b) {{
                return dateToSortKey(a.date).localeCompare(dateToSortKey(b.date));
            }});

            sells.forEach(function(s) {{
                var gain = (s.sellPrice - s.avgBuyPrice) * s.shares;
                var gainColor = gain >= 0 ? 'text-emerald-400' : 'text-red-400';
                var gainText = (gain >= 0 ? '+' : '') + gain.toFixed(2) + ' €';

                // Haupt-Verkaufszeile
                var tr = document.createElement('tr');
                tr.className = 'border-l-2 border-red-500 border-b border-gray-700 bg-gray-900';
                tr.innerHTML = '<td class="py-2 pl-2 pr-3 font-medium">' + s.date + '</td>'
                    + '<td class="py-2 pr-3 text-red-400 font-semibold">Verkauf</td>'
                    + '<td class="py-2 pr-3 text-right">' + parseFloat(s.sellPrice).toFixed(2) + ' €</td>'
                    + '<td class="py-2 pr-3 text-right">' + fmtShares(s.shares) + '</td>'
                    + '<td class="py-2 pr-3 text-right">' + (s.amount != null ? parseFloat(s.amount).toFixed(2) + ' €' : '—') + '</td>'
                    + '<td class="py-2 pr-3 text-right ' + gainColor + '">' + gainText + '</td>'
                    + '<td class="py-2 text-right">' + (s.taxes ? parseFloat(s.taxes).toFixed(2) + ' €' : '—') + '</td>';
                body.appendChild(tr);

                // FIFO-Sub-Zeilen (eingerückt)
                (s.fifoDetails || []).forEach(function(fd) {{
                    var fdGain = (s.sellPrice - fd.buyPrice) * fd.shares;
                    var fdColor = fdGain >= 0 ? 'text-emerald-400' : 'text-red-400';
                    var sub = document.createElement('tr');
                    sub.className = 'border-l-2 border-emerald-700 border-b border-gray-800 bg-gray-950 text-gray-400';
                    sub.innerHTML = '<td class="py-1 pl-6 pr-3 text-xs">↳ Charge: ' + (fd.buyDate || '—') + '</td>'
                        + '<td class="py-1 pr-3 text-xs text-emerald-600">Kauf</td>'
                        + '<td class="py-1 pr-3 text-right text-xs">' + parseFloat(fd.buyPrice).toFixed(2) + ' €</td>'
                        + '<td class="py-1 pr-3 text-right text-xs">' + fmtShares(fd.shares) + '</td>'
                        + '<td class="py-1 pr-3 text-right text-xs">—</td>'
                        + '<td class="py-1 pr-3 text-right text-xs ' + fdColor + '">' + (fdGain >= 0 ? '+' : '') + fdGain.toFixed(2) + ' €</td>'
                        + '<td class="py-1 text-right text-xs">—</td>';
                    body.appendChild(sub);
                }});
            }});

            // ── Trennlinie + Offene Positionen ────────────────────────────
            var portfolio = (asset.portfolio || []).slice().sort(function(a, b) {{
                return dateToSortKey(a.date).localeCompare(dateToSortKey(b.date));
            }});

            if (portfolio.length > 0) {{
                var sepRow = document.createElement('tr');
                sepRow.innerHTML = '<td colspan="7" class="py-2 pl-2 text-xs font-semibold text-indigo-400 uppercase tracking-wide border-t border-gray-700 bg-gray-900">Offene Positionen (noch im Bestand)</td>';
                body.appendChild(sepRow);

                portfolio.forEach(function(p) {{
                    var tr2 = document.createElement('tr');
                    tr2.className = 'border-l-2 border-emerald-500 border-b border-gray-800';
                    tr2.innerHTML = '<td class="py-2 pl-2 pr-3">' + p.date + '</td>'
                        + '<td class="py-2 pr-3 text-emerald-400 font-semibold">Kauf</td>'
                        + '<td class="py-2 pr-3 text-right">' + parseFloat(p.buyPrice).toFixed(2) + ' €</td>'
                        + '<td class="py-2 pr-3 text-right">' + fmtShares(p.shares) + '</td>'
                        + '<td class="py-2 pr-3 text-right">' + (p.amount != null ? parseFloat(p.amount).toFixed(2) + ' €' : '—') + '</td>'
                        + '<td class="py-2 pr-3 text-right text-gray-500">im Bestand</td>'
                        + '<td class="py-2 text-right">—</td>';
                    body.appendChild(tr2);
                }});
            }}

            if (sells.length === 0 && portfolio.length === 0) {{
                body.innerHTML = '<tr><td colspan="7" class="py-4 text-center text-gray-500">Keine Transaktionen</td></tr>';
            }}
        }}

        function reentryPopulateSells(sells) {{
            var sel = document.getElementById('reentry-sell-select');
            sel.innerHTML = '<option value="">— Verkauf wählen (oder manuell eingeben) —</option>';
            (sells || []).forEach(function(s, i) {{
                var opt = document.createElement('option');
                opt.value = i;
                opt.textContent = s.date + ' · ' + parseFloat(s.sellPrice).toFixed(2) + ' € · ' + s.shares + ' Stk';
                sel.appendChild(opt);
            }});
            document.getElementById('reentry-result').classList.add('hidden');
            reentryRenderFifoDetails([]);
            document.getElementById('reentry-sell-price').value = '';
            document.getElementById('reentry-shares').value = '';
            document.getElementById('reentry-tax').value = '';
            document.getElementById('reentry-fee').value = '0';
            document.getElementById('reentry-extra').value = '0';
            document.getElementById('reentry-kirche').value = '0';
            document.getElementById('reentry-note').value = '';
            document.getElementById('reentry-saved-area').classList.add('hidden');
            document.getElementById('reentry-saved-list').innerHTML = '';
            window._ruentrySells = sells || [];
            window._reentryAsset = window._currentAsset;
            simInitPanel(window._reentryAsset);
        }}

        function reentryOnSelectChange() {{
            var idx = document.getElementById('reentry-sell-select').value;
            if (idx === '') {{ reentryRenderFifoDetails([]); return; }}
            var s = window._ruentrySells[parseInt(idx)];
            document.getElementById('reentry-sell-price').value = parseFloat(s.sellPrice).toFixed(2);
            document.getElementById('reentry-shares').value = s.shares;
            document.getElementById('reentry-tax').value = s.taxes ? parseFloat(s.taxes).toFixed(2) : '0';
            reentryCalc();
            reentryRenderFifoDetails(s.fifoDetails || [], parseFloat(s.sellPrice) || 0);
        }}

        function simTotalShares() {{
            var asset = window._reentryAsset;
            if (!asset || !asset.portfolio) return 0;
            return asset.portfolio.reduce(function(s, l) {{ return s + parseFloat(l.shares || 0); }}, 0);
        }}

        function simSetAll() {{
            var total = simTotalShares();
            document.getElementById('sim-shares').value = total > 0 ? total : '';
            simUpdate();
        }}

        function simUpdate() {{
            var total = simTotalShares();
            var entered = parseFloat(document.getElementById('sim-shares').value) || 0;
            var targetPrice = parseFloat(document.getElementById('sim-target-price').value) || 0;
            var remaining = total - entered;
            var remEl = document.getElementById('sim-remaining');
            var warnEl = document.getElementById('sim-warn-overstock');
            if (entered > 0) {{
                remEl.classList.remove('hidden');
                document.getElementById('sim-remaining-val').textContent =
                    (remaining >= 0 ? remaining : 0).toFixed(4).replace(/\\.?0+$/, '') + ' Stk';
                warnEl.classList.toggle('hidden', remaining >= 0);
            }} else {{
                remEl.classList.add('hidden');
                warnEl.classList.add('hidden');
            }}
            // FIFO-Vorschau rendern wenn beide Felder gefüllt
            if (targetPrice > 0 && entered > 0) {{
                simRenderFifoTable(targetPrice, entered);
            }} else {{
                var lotsEl = document.getElementById('reentry-simulate-lots');
                if (lotsEl) lotsEl.innerHTML = '';
            }}
        }}

        function simRenderFifoTable(targetPrice, wantedShares) {{
            var lotsEl = document.getElementById('reentry-simulate-lots');
            if (!lotsEl) return;
            var asset = window._reentryAsset;
            if (!asset || !asset.portfolio || asset.portfolio.length === 0) {{ lotsEl.innerHTML = ''; return; }}
            var kirche = parseFloat(document.getElementById('reentry-kirche').value) || 0;
            var taxRate = 0.25 * (1 + 0.055 + kirche);

            var remaining = wantedShares;
            var rows = [];
            var totalGain = 0, totalTax = 0, totalShares = 0;

            asset.portfolio.forEach(function(lot) {{
                if (remaining <= 0) return;
                var lotShares = parseFloat(lot.shares) || 0;
                var affected = Math.min(lotShares, remaining);
                remaining -= affected;
                var gain = (targetPrice - parseFloat(lot.buyPrice)) * affected;
                var tax = gain > 0 ? gain * taxRate : 0;
                totalGain += gain;
                totalTax += tax;
                totalShares += affected;
                var gainColor = gain >= 0 ? 'text-emerald-400' : 'text-red-400';
                rows.push('<tr class="border-t border-gray-700">'
                    + '<td class="py-1 px-2 text-gray-400">' + (lot.date || '') + '</td>'
                    + '<td class="py-1 px-2 text-right">' + parseFloat(lot.buyPrice).toFixed(2) + ' €</td>'
                    + '<td class="py-1 px-2 text-right">' + affected.toFixed(4).replace(/\\.?0+$/, '') + '</td>'
                    + '<td class="py-1 px-2 text-right ' + gainColor + '">' + (gain >= 0 ? '+' : '') + gain.toFixed(2) + ' €</td>'
                    + '<td class="py-1 px-2 text-right text-yellow-400">' + tax.toFixed(2) + ' €</td>'
                    + '</tr>');
            }});

            var nettoErloes = targetPrice * totalShares - totalTax;
            var sumGainColor = totalGain >= 0 ? 'text-emerald-400' : 'text-red-400';
            var sumRow = '<tr class="border-t-2 border-gray-500 font-semibold">'
                + '<td class="py-1 px-2 text-gray-300" colspan="3">Gesamt</td>'
                + '<td class="py-1 px-2 text-right ' + sumGainColor + '">' + (totalGain >= 0 ? '+' : '') + totalGain.toFixed(2) + ' €</td>'
                + '<td class="py-1 px-2 text-right text-yellow-400">' + totalTax.toFixed(2) + ' €</td>'
                + '</tr>';

            lotsEl.innerHTML = '<div class="mt-3">'
                + '<p class="text-xs text-gray-400 mb-1">FIFO-Vorschau (älteste Chargen zuerst)</p>'
                + '<table class="w-full text-xs mb-2">'
                + '<thead><tr class="text-gray-500">'
                + '<th class="py-1 px-2 text-left">Kaufdatum</th>'
                + '<th class="py-1 px-2 text-right">Kaufkurs</th>'
                + '<th class="py-1 px-2 text-right">Stück</th>'
                + '<th class="py-1 px-2 text-right">Gewinn</th>'
                + '<th class="py-1 px-2 text-right">Steuer</th>'
                + '</tr></thead>'
                + '<tbody>' + rows.join('') + sumRow + '</tbody>'
                + '</table>'
                + '<div class="text-xs text-gray-400 mb-3">Netto-Erlös (nach Steuer): <span class="text-white font-medium">' + nettoErloes.toFixed(2) + ' €</span></div>'
                + '<button onclick="simSave(' + targetPrice + ',' + totalShares.toFixed(4) + ',' + totalGain.toFixed(2) + ',' + totalTax.toFixed(2) + ',' + nettoErloes.toFixed(2) + ')" '
                + 'class="text-xs bg-indigo-600 hover:bg-indigo-700 rounded-lg px-4 py-2 text-white font-medium transition-colors">In Analyse speichern</button>'
                + '</div>';
        }}

        function simSave(targetPrice, shares, gain, tax, netto) {{
            var asset = window._reentryAsset;
            var name = asset ? (asset.company_name || '') : '';
            var note = '';
            var entry = {{
                date: new Date().toLocaleDateString('de-DE'),
                asset: name,
                sellPrice: targetPrice, shares: shares, tax: tax, fee: 0, extra: 0,
                breakeven: '— (Simulation)',
                dropPct: '—',
                target: targetPrice.toFixed(2) + ' €',
                note: 'Simulation: Gewinn ' + (gain >= 0 ? '+' : '') + gain.toFixed(2) + ' €, Netto ' + netto.toFixed(2) + ' €'
            }};
            var saved = document.getElementById('reentry-saved-area');
            var list  = document.getElementById('reentry-saved-list');
            var card = document.createElement('div');
            card.className = 'reentry-card bg-gray-900 border border-gray-700 rounded-lg p-3 text-xs';
            card.innerHTML = '<div class="flex justify-between items-start">'
                + '<span class="text-gray-400">' + entry.date + ' · ' + name + ' · Simulation</span>'
                + '<button onclick="reentryDeleteCard(this)" class="text-gray-600 hover:text-red-400 ml-2">✕</button>'
                + '</div>'
                + '<div class="mt-1 text-white">'
                + 'Zielkurs: <b>' + targetPrice.toFixed(2) + ' €</b> · '
                + 'Stück: <b>' + shares + '</b> · '
                + 'Gewinn: <b>' + (gain >= 0 ? '+' : '') + gain.toFixed(2) + ' €</b> · '
                + 'Steuer: <b>' + tax.toFixed(2) + ' €</b> · '
                + 'Netto: <b>' + netto.toFixed(2) + ' €</b>'
                + '</div>';
            list.appendChild(card);
            saved.classList.remove('hidden');
        }}

        function simInitPanel(asset) {{
            var total = simTotalShares();
            var noPos = document.getElementById('reentry-simulate-no-positions');
            var inputs = document.getElementById('reentry-simulate-inputs');
            if (!asset || !asset.portfolio || asset.portfolio.length === 0) {{
                noPos.classList.remove('hidden');
                inputs.classList.add('hidden');
            }} else {{
                noPos.classList.add('hidden');
                inputs.classList.remove('hidden');
                var fmtTotal = total.toFixed(4).replace(/\\.?0+$/, '');
                document.getElementById('sim-all-btn').textContent = 'Gesamten Bestand (' + fmtTotal + ' Stk)';
                document.getElementById('sim-target-price').value = '';
                document.getElementById('sim-shares').value = '';
                document.getElementById('sim-remaining').classList.add('hidden');
                document.getElementById('sim-warn-overstock').classList.add('hidden');
                // Live-Kurs vorbelegen falls vorhanden
                var liveEl = document.getElementById('detail-live-price');
                if (liveEl && liveEl.value) {{
                    document.getElementById('sim-target-price').value = parseFloat(liveEl.value).toFixed(2);
                }}
            }}
        }}

        function reentrySetMode(mode) {{
            var isHistoric = mode === 'historic';
            document.getElementById('reentry-historic-panel').style.display = isHistoric ? '' : 'none';
            document.getElementById('reentry-simulate-panel').classList.toggle('hidden', isHistoric);
            document.getElementById('reentry-tab-historic').className = 'text-xs px-4 py-2 rounded-t-lg font-medium transition-colors '
                + (isHistoric ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-white');
            document.getElementById('reentry-tab-simulate').className = 'text-xs px-4 py-2 rounded-t-lg font-medium transition-colors '
                + (!isHistoric ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-white');
            // Ergebnis-Panel und FIFO-Tabelle verstecken beim Wechsel
            if (!isHistoric) {{
                document.getElementById('reentry-result').classList.add('hidden');
                reentryRenderFifoDetails([]);
            }}
        }}

        function reentryRenderFifoDetails(lots, sellPrice) {{
            var box = document.getElementById('reentry-fifo-details');
            if (!box) return;
            if (!lots || lots.length === 0) {{ box.classList.add('hidden'); return; }}
            var kirche = parseFloat(document.getElementById('reentry-kirche').value) || 0;
            var taxRate = 0.25 * (1 + 0.055 + kirche);
            var totalGain = 0, totalTax = 0;
            var rows = lots.map(function(fd) {{
                var gain = (sellPrice - parseFloat(fd.buyPrice)) * parseFloat(fd.shares);
                var tax  = gain > 0 ? gain * taxRate : 0;
                totalGain += gain;
                totalTax  += tax;
                var gainColor = gain >= 0 ? 'text-emerald-400' : 'text-red-400';
                return '<tr class="border-t border-gray-700">'
                    + '<td class="py-1 px-2 text-gray-400">' + (fd.buyDate || '') + '</td>'
                    + '<td class="py-1 px-2 text-right">' + parseFloat(fd.buyPrice).toFixed(2) + ' €</td>'
                    + '<td class="py-1 px-2 text-right">' + parseFloat(fd.shares).toFixed(4).replace(/\\.?0+$/, '') + '</td>'
                    + '<td class="py-1 px-2 text-right ' + gainColor + '">' + (gain >= 0 ? '+' : '') + gain.toFixed(2) + ' €</td>'
                    + '<td class="py-1 px-2 text-right text-yellow-400">' + tax.toFixed(2) + ' €</td>'
                    + '</tr>';
            }});
            var gainColor = totalGain >= 0 ? 'text-emerald-400' : 'text-red-400';
            var sumRow = '<tr class="border-t-2 border-gray-500 font-semibold">'
                + '<td class="py-1 px-2 text-gray-300" colspan="3">Gesamt</td>'
                + '<td class="py-1 px-2 text-right ' + gainColor + '">' + (totalGain >= 0 ? '+' : '') + totalGain.toFixed(2) + ' €</td>'
                + '<td class="py-1 px-2 text-right text-yellow-400">' + totalTax.toFixed(2) + ' €</td>'
                + '</tr>';
            box.innerHTML = '<div class="mt-3">'
                + '<p class="text-xs text-gray-400 mb-1">Aufgelöste FIFO-Chargen</p>'
                + '<table class="w-full text-xs">'
                + '<thead><tr class="text-gray-500">'
                + '<th class="py-1 px-2 text-left">Kaufdatum</th>'
                + '<th class="py-1 px-2 text-right">Kaufkurs</th>'
                + '<th class="py-1 px-2 text-right">Stück</th>'
                + '<th class="py-1 px-2 text-right">Gewinn</th>'
                + '<th class="py-1 px-2 text-right">Steuer</th>'
                + '</tr></thead>'
                + '<tbody>' + rows.join('') + sumRow + '</tbody>'
                + '</table></div>';
            box.classList.remove('hidden');
        }}

        function reentryAutoTax() {{
            var sellPrice = parseFloat(document.getElementById('reentry-sell-price').value) || 0;
            var shares    = parseFloat(document.getElementById('reentry-shares').value) || 0;
            var kirche    = parseFloat(document.getElementById('reentry-kirche').value) || 0;
            if (sellPrice <= 0 || shares <= 0) return;

            // Kaufpreis aus gewähltem Verkauf oder 0
            var idx = document.getElementById('reentry-sell-select').value;
            var avgBuy = 0;
            if (idx !== '') {{
                var s = window._ruentrySells[parseInt(idx)];
                avgBuy = parseFloat(s.avgBuyPrice) || 0;
            }}
            var gewinn = (sellPrice - avgBuy) * shares;
            if (gewinn <= 0) {{ document.getElementById('reentry-tax').value = '0'; reentryCalc(); return; }}

            // Abgeltung 25% + Soli 5,5% auf Steuer + Kirchensteuer auf Steuer
            var abgeltung = gewinn * 0.25;
            var soli      = abgeltung * 0.055;
            var kst       = abgeltung * kirche;
            var steuer    = abgeltung + soli + kst;
            document.getElementById('reentry-tax').value = steuer.toFixed(2);
            reentryCalc();
        }}

        function reentryCalc() {{
            var sellPrice = parseFloat(document.getElementById('reentry-sell-price').value) || 0;
            var shares    = parseFloat(document.getElementById('reentry-shares').value) || 0;
            var tax       = parseFloat(document.getElementById('reentry-tax').value) || 0;
            var fee       = parseFloat(document.getElementById('reentry-fee').value) || 0;
            var extra     = parseFloat(document.getElementById('reentry-extra').value) || 0;

            if (sellPrice <= 0 || shares <= 0) {{
                document.getElementById('reentry-result').classList.add('hidden');
                return;
            }}

            var bruttoErloes = sellPrice * shares;
            var nettoErloes  = bruttoErloes - tax;
            var breakeven    = (nettoErloes - fee) / shares;
            var targetPrice  = (nettoErloes - fee + extra) / shares;
            var dropPct      = ((breakeven - sellPrice) / sellPrice) * 100;  // negativ = muss fallen

            document.getElementById('reentry-net').textContent      = nettoErloes.toFixed(2) + ' €';
            document.getElementById('reentry-breakeven').textContent = breakeven.toFixed(2) + ' €';
            document.getElementById('reentry-drop-pct').textContent  =
                (dropPct <= 0 ? '' : '+') + dropPct.toFixed(1) + ' %'
                + (dropPct < 0 ? ' ↓' : ' ↑');
            document.getElementById('reentry-target').textContent    = targetPrice.toFixed(2) + ' €';
            document.getElementById('reentry-gain').textContent      = (extra >= 0 ? '+' : '') + extra.toFixed(2) + ' €';
            document.getElementById('reentry-hint').textContent      =
                'Der Kurs muss um ' + Math.abs(dropPct).toFixed(1) + ' % sinken (auf ' + breakeven.toFixed(2) +
                ' €), damit du zu Verkaufskonditionen wieder einsteigst und Steuer + Gebühren bereits verdient hast.';
            document.getElementById('reentry-result').classList.remove('hidden');
        }}

        function reentrySave() {{
            var sellPrice = parseFloat(document.getElementById('reentry-sell-price').value) || 0;
            var shares    = parseFloat(document.getElementById('reentry-shares').value) || 0;
            var tax       = parseFloat(document.getElementById('reentry-tax').value) || 0;
            var fee       = parseFloat(document.getElementById('reentry-fee').value) || 0;
            var extra     = parseFloat(document.getElementById('reentry-extra').value) || 0;
            var note      = document.getElementById('reentry-note').value.trim();
            var breakeven = document.getElementById('reentry-breakeven').textContent;
            var dropPct   = document.getElementById('reentry-drop-pct').textContent;
            var target    = document.getElementById('reentry-target').textContent;

            if (sellPrice <= 0 || shares <= 0) return;

            var entry = {{
                date: new Date().toLocaleDateString('de-DE'),
                asset: window._reentryAsset ? window._reentryAsset.company_name || '' : '',
                sellPrice: sellPrice, shares: shares, tax: tax, fee: fee, extra: extra,
                breakeven: breakeven, dropPct: dropPct, target: target, note: note
            }};

            var card = document.createElement('div');
            card.className = 'reentry-card bg-gray-900 border border-gray-700 rounded-lg p-3 text-xs';
            card.innerHTML =
                '<div class="flex justify-between items-start mb-1">'
                + '<span class="font-medium text-white">' + entry.date + ' · ' + entry.sellPrice.toFixed(2) + ' € · ' + entry.shares + ' Stk</span>'
                + '<button onclick="reentryDeleteCard(this)" class="text-gray-600 hover:text-red-400 ml-2">✕</button>'
                + '</div>'
                + '<div class="grid grid-cols-3 gap-2 mb-2 text-gray-300">'
                + '<span>Break-Even: <strong class="text-indigo-400">' + entry.breakeven + '</strong></span>'
                + '<span>Muss sinken: <strong class="text-amber-400">' + entry.dropPct + '</strong></span>'
                + '<span>Ziel-Kurs: <strong class="text-emerald-400">' + entry.target + '</strong></span>'
                + '</div>'
                + (note ? '<p class="text-gray-400 italic">' + note + '</p>' : '');

            document.getElementById('reentry-saved-list').appendChild(card);
            document.getElementById('reentry-saved-area').classList.remove('hidden');
            document.getElementById('reentry-note').value = '';
        }}

        function reentryDeleteCard(btn) {{
            btn.closest('.reentry-card').remove();
            if (!document.getElementById('reentry-saved-list').children.length) {{
                document.getElementById('reentry-saved-area').classList.add('hidden');
            }}
        }}

        function showOverview() {{
            document.getElementById('detail-view').style.display = 'none';
            document.getElementById('portfolio-view').style.display = 'block';
        }}

        // ── Init ─────────────────────────────────────────────────────────
        renderSummary();
        setFilter('all');
        setSort('return');
    </script>

</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Multi-Asset HTML-Report erstellt: {output_path}")
    print(f"   {len(analyzers_dict)} Aktien · Summary: invested={total_invested:,.0f} · realized={total_realized_gains:,.0f}")

    try:
        _open_in_chrome(output_path)
        print(f"🌐 Report im Browser geöffnet")
    except Exception:
        print(f"💡 Öffne die Datei manuell im Browser: {output_path}")

    return output_path


def analyze_portfolio_from_csv(csv_file_path, current_price=None, currency="EUR"):
    """
    Multi-Asset Portfolio-Analyse: liest eine CSV mit mehreren Aktien ein und erstellt
    für jede Aktie eine eigene PortfolioFIFOAnalyzer-Instanz.

    Args:
        csv_file_path (str): Pfad zur CSV-Datei
        current_price (float, optional): Aktueller Kurs (wird für alle Aktien verwendet)
        currency (str): Währung (Standard: EUR)

    Returns:
        dict: { holdingname: PortfolioFIFOAnalyzer } für jede erkannte Aktie
    """
    # CSV einmalig einlesen (Trennzeichen automatisch erkennen)
    _tmp = PortfolioFIFOAnalyzer.__new__(PortfolioFIFOAnalyzer)
    _tmp.csv_file_path = csv_file_path

    delimiter = _tmp._detect_delimiter(csv_file_path)
    try:
        raw = pd.read_csv(csv_file_path, delimiter=delimiter, encoding='utf-8')
    except Exception:
        raw = pd.read_csv(csv_file_path, delimiter=delimiter, encoding='latin-1')

    print(f"CSV geladen: {len(raw)} Transaktionen gesamt")

    # holdingname-Spalte finden (case-insensitive)
    holding_col = None
    for col in raw.columns:
        if col.lower().strip() in ('holdingname', 'unternehmen', 'name', 'company_name'):
            holding_col = col
            break

    if holding_col is None:
        raise ValueError("Keine Spalte fuer Aktiennamen gefunden (holdingname / unternehmen / name).")

    holdings = sorted(raw[holding_col].dropna().unique())
    print(f"{len(holdings)} Aktien erkannt")

    analyzers = {}
    failed = []
    for holding in holdings:
        df_filtered = raw[raw[holding_col] == holding].copy()
        try:
            analyzer = PortfolioFIFOAnalyzer(
                csv_file_path=csv_file_path,
                current_price=current_price,
                currency=currency,
                _preloaded_df=df_filtered,
            )
            analyzers[holding] = analyzer
        except Exception as exc:
            failed.append((holding, str(exc)))

    if failed:
        print(f"  {len(failed)} Aktien konnten nicht analysiert werden (z.B. keine Kaeufe):")
        for name, err in failed:
            print(f"    - {name}: {err}")

    print(f"Analyse abgeschlossen: {len(analyzers)} von {len(holdings)} Aktien erfolgreich")
    return analyzers


# BEISPIEL-VERWENDUNG
if __name__ == "__main__":
    print("PORTFOLIO FIFO ANALYZER - Multi-Asset")
    print("=" * 50)

    csv_file = "csvs/Chris-20260606-153648.csv"
    currency = "EUR"

    try:
        analyzers = analyze_portfolio_from_csv(csv_file, currency=currency)

        print(f"\n{len(analyzers)} Aktien erkannt und analysiert")

        generate_multi_asset_report(analyzers)

    except FileNotFoundError:
        print(f"CSV-Datei nicht gefunden: {csv_file}")
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
