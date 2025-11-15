#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests für FIFO-Analyse und Gewinn-Berechnung

Diese Tests definieren die erwartete Funktionalität für die _perform_fifo_analysis() Methode.
Sie sind als xfail markiert, bis die Implementierung erfolgt ist.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from portfolio_analyzer import PortfolioFIFOAnalyzer


class TestBasicFIFOLogic:
    """Tests für die grundlegende FIFO-Logik"""

    @pytest.mark.xfail(reason="FIFO analysis not yet implemented", strict=False)
    def test_simple_fifo_single_buy_single_sell(self, temp_csv_file):
        """
        Test einfachstes FIFO-Szenario: Ein Kauf, ein Verkauf

        Kauf:  10 Aktien @ 50 = 500
        Verkauf: 8 Aktien @ 60 = 480
        Erwarteter Gewinn: (8 * 60) - (8 * 50) = 480 - 400 = 80
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-15,Sell,8,60.00,480.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Überprüfe dass FIFO korrekt durchgeführt wurde
        assert len(analyzer.portfolio) == 1  # Eine verbleibende Position
        assert analyzer.portfolio[0]['shares'] == 2  # 10 - 8 = 2 verbleibend
        assert analyzer.portfolio[0]['price'] == 50.00  # Ursprünglicher Kaufpreis

    @pytest.mark.xfail(reason="FIFO analysis not yet implemented", strict=False)
    def test_fifo_multiple_buys_single_sell(self, temp_csv_file):
        """
        Test FIFO mit mehreren Käufen und einem Verkauf

        Kauf 1: 10 Aktien @ 50 = 500
        Kauf 2: 15 Aktien @ 55 = 825
        Verkauf: 8 Aktien @ 60 = 480

        FIFO: Die 8 ältesten Aktien (aus Kauf 1) werden verkauft
        Verbleibend:
        - 2 Aktien @ 50 (Rest von Kauf 1)
        - 15 Aktien @ 55 (Kauf 2 komplett)
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-20,Buy,15,55.00,825.00,0.00,TestCorp
2024-03-10,Sell,8,60.00,480.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Verbleibende Aktien: 10 + 15 - 8 = 17
        total_remaining = sum(pos['shares'] for pos in analyzer.portfolio)
        assert total_remaining == 17

    @pytest.mark.xfail(reason="FIFO analysis not yet implemented", strict=False)
    def test_fifo_sell_spans_multiple_purchases(self, temp_csv_file):
        """
        Test FIFO wenn Verkauf mehrere Käufe umspannt

        Kauf 1: 10 Aktien @ 50 = 500
        Kauf 2: 15 Aktien @ 55 = 825
        Verkauf: 20 Aktien @ 60

        FIFO: 10 aus Kauf 1 + 10 aus Kauf 2
        Verbleibend: 5 Aktien @ 55 (Rest von Kauf 2)
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-20,Buy,15,55.00,825.00,0.00,TestCorp
2024-03-10,Sell,20,60.00,1200.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        total_remaining = sum(pos['shares'] for pos in analyzer.portfolio)
        assert total_remaining == 5

        # Die verbleibenden 5 sollten aus dem zweiten Kauf sein
        remaining_positions = [pos for pos in analyzer.portfolio if pos['shares'] > 0]
        assert len(remaining_positions) == 1
        assert remaining_positions[0]['price'] == 55.00


class TestRealizedGainsCalculation:
    """Tests für die Berechnung realisierter Gewinne"""

    @pytest.mark.xfail(reason="FIFO analysis not yet implemented", strict=False)
    def test_calculates_gross_realized_gains(self, temp_csv_file):
        """
        Test Berechnung der Brutto-Gewinne

        Kauf:  10 @ 50 = 500
        Verkauf: 8 @ 60 = 480
        Brutto-Gewinn: (8 * 60) - (8 * 50) = 80
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-15,Sell,8,60.00,480.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Die Analyse sollte den realisierten Gewinn berechnet haben
        assert 'total_realized_gains' in analyzer.analysis_results
        assert analyzer.analysis_results['total_realized_gains'] == 80.00

    @pytest.mark.xfail(reason="FIFO analysis not yet implemented", strict=False)
    def test_calculates_net_realized_gains_after_tax(self, temp_csv_file):
        """
        Test Berechnung der Netto-Gewinne (nach Steuern)

        Kauf:  10 @ 50 = 500
        Verkauf: 8 @ 60 = 480
        Steuern: 20
        Brutto-Gewinn: 80
        Netto-Gewinn: 80 - 20 = 60
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-15,Sell,8,60.00,480.00,20.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        assert analyzer.analysis_results['total_realized_gains'] == 80.00
        assert analyzer.analysis_results['total_taxes'] == 20.00
        assert analyzer.analysis_results['net_realized_gains'] == 60.00

    @pytest.mark.xfail(reason="FIFO analysis not yet implemented", strict=False)
    def test_handles_realized_losses(self, temp_csv_file):
        """
        Test Behandlung von Verlusten

        Kauf:  10 @ 60 = 600
        Verkauf: 8 @ 50 = 400
        Verlust: (8 * 50) - (8 * 60) = 400 - 480 = -80
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,60.00,600.00,0.00,TestCorp
2024-02-15,Sell,8,50.00,400.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Sollte negativen Gewinn (= Verlust) berechnen
        assert analyzer.analysis_results['total_realized_gains'] == -80.00

    @pytest.mark.xfail(reason="FIFO analysis not yet implemented", strict=False)
    def test_multiple_sell_transactions_accumulate_gains(self, temp_csv_file):
        """
        Test dass mehrere Verkäufe die Gewinne akkumulieren

        Kauf 1: 100 @ 10 = 1000
        Verkauf 1: 30 @ 15 = 450, Gewinn: (30 * 15) - (30 * 10) = 150
        Verkauf 2: 40 @ 20 = 800, Gewinn: (40 * 20) - (40 * 10) = 400
        Gesamt-Gewinn: 150 + 400 = 550
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,100,10.00,1000.00,0.00,TestCorp
2024-02-15,Sell,30,15.00,450.00,0.00,TestCorp
2024-03-15,Sell,40,20.00,800.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        assert analyzer.analysis_results['total_realized_gains'] == 550.00


class TestUnrealizedGains:
    """Tests für die Berechnung unrealisierter Gewinne"""

    @pytest.mark.xfail(reason="FIFO analysis not yet implemented", strict=False)
    def test_calculates_unrealized_gains_for_remaining_shares(self, temp_csv_file):
        """
        Test Berechnung unrealisierter Gewinne

        Kauf: 10 @ 50 = 500
        Aktueller Preis: 70
        Unrealisierter Gewinn: (10 * 70) - 500 = 700 - 500 = 200
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file), current_price=70.0)

        assert 'unrealized_gains' in analyzer.analysis_results
        assert analyzer.analysis_results['unrealized_gains'] == 200.00

    @pytest.mark.xfail(reason="FIFO analysis not yet implemented", strict=False)
    def test_unrealized_gains_with_multiple_positions(self, temp_csv_file):
        """
        Test unrealisierte Gewinne bei mehreren Positionen

        Kauf 1: 10 @ 50 = 500
        Kauf 2: 15 @ 55 = 825
        Verkauf: 8 @ 60
        Verbleibend: 2 @ 50 + 15 @ 55 = 100 + 825 = 925

        Aktueller Preis: 70
        Aktueller Wert: 17 * 70 = 1190
        Unrealisierter Gewinn: 1190 - 925 = 265
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-20,Buy,15,55.00,825.00,0.00,TestCorp
2024-03-10,Sell,8,60.00,480.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file), current_price=70.0)

        # Verbleibende Cost Basis: (2 * 50) + (15 * 55) = 100 + 825 = 925
        # Aktueller Wert: 17 * 70 = 1190
        # Unrealisierter Gewinn: 1190 - 925 = 265
        assert analyzer.analysis_results['unrealized_gains'] == 265.00


class TestComplexScenarios:
    """Tests für komplexere FIFO-Szenarien"""

    @pytest.mark.xfail(reason="FIFO analysis not yet implemented", strict=False)
    def test_complex_portfolio_with_multiple_buys_sells(self, temp_csv_file, complex_portfolio_csv_content):
        """Test komplexes Portfolio mit vielen Transaktionen"""
        temp_csv_file.write_text(complex_portfolio_csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file), current_price=25.0)

        # Überprüfe dass alle Transaktionen verarbeitet wurden
        assert analyzer.transactions is not None
        assert len(analyzer.transactions) == 7

        # Überprüfe dass die Analyse durchgeführt wurde
        assert 'total_invested' in analyzer.analysis_results
        assert 'total_realized_gains' in analyzer.analysis_results

    @pytest.mark.xfail(reason="FIFO analysis not yet implemented", strict=False)
    def test_complete_liquidation(self, temp_csv_file):
        """
        Test vollständige Liquidation (alle Aktien verkauft)

        Kauf 1: 10 @ 50
        Kauf 2: 5 @ 55
        Verkauf: 15 @ 60

        Verbleibende Aktien: 0
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-20,Buy,5,55.00,275.00,0.00,TestCorp
2024-03-10,Sell,15,60.00,900.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Portfolio sollte leer sein
        total_remaining = sum(pos['shares'] for pos in analyzer.portfolio if pos['shares'] > 0)
        assert total_remaining == 0

        # Sollte trotzdem korrekte Gewinne berechnen
        # Gewinn: (10 * 60 + 5 * 60) - (10 * 50 + 5 * 55) = 900 - 775 = 125
        assert analyzer.analysis_results['total_realized_gains'] == 125.00

    @pytest.mark.xfail(reason="FIFO analysis not yet implemented", strict=False)
    def test_chronological_order_respected(self, temp_csv_file):
        """
        Test dass chronologische Reihenfolge respektiert wird

        Wichtig: Auch wenn CSV nicht sortiert ist, sollte FIFO nach Datum erfolgen
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-03-15,Buy,10,60.00,600.00,0.00,TestCorp
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-20,Sell,8,70.00,560.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Der Verkauf am 2024-02-20 sollte die ältesten Aktien nehmen (2024-01-15)
        # Auch wenn sie in der CSV später kommen
        # Gewinn: (8 * 70) - (8 * 50) = 560 - 400 = 160
        assert analyzer.analysis_results['total_realized_gains'] == 160.00


class TestEdgeCases:
    """Tests für Sonderfälle und Grenzfälle"""

    @pytest.mark.xfail(reason="FIFO analysis not yet implemented", strict=False)
    def test_sell_more_than_owned_raises_error(self, temp_csv_file):
        """Test dass Verkauf von mehr Aktien als vorhanden einen Fehler verursacht"""
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-15,Sell,15,60.00,900.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)

        with pytest.raises(Exception):  # ValueError erwartet
            analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

    @pytest.mark.xfail(reason="FIFO analysis not yet implemented", strict=False)
    def test_sell_before_buy_raises_error(self, temp_csv_file):
        """Test dass Verkauf vor Kauf einen Fehler verursacht"""
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Sell,5,60.00,300.00,0.00,TestCorp
2024-02-15,Buy,10,50.00,500.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)

        with pytest.raises(Exception):  # ValueError erwartet
            analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

    @pytest.mark.xfail(reason="FIFO analysis not yet implemented", strict=False)
    def test_zero_shares_transaction_ignored(self, temp_csv_file):
        """Test dass Transaktionen mit 0 Aktien ignoriert werden"""
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-15,Buy,0,55.00,0.00,0.00,TestCorp
2024-03-15,Sell,5,60.00,300.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Sollte die Null-Transaktion ignorieren
        total_remaining = sum(pos['shares'] for pos in analyzer.portfolio if pos['shares'] > 0)
        assert total_remaining == 5  # 10 - 5 = 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
