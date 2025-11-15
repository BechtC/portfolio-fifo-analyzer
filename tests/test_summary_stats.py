#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests für Summary Statistics Berechnung

Diese Tests definieren die erwartete Funktionalität für die _calculate_summary_stats() Methode.
Sie sind als xfail markiert, bis die Implementierung erfolgt ist.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from portfolio_analyzer import PortfolioFIFOAnalyzer


class TestSummaryStatsCalculation:
    """Tests für die Berechnung der Summary Statistics"""

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_calculates_total_invested(self, temp_csv_file):
        """
        Test Berechnung der Gesamt-Investition

        Alle Buy-Transaktionen aufsummiert
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-20,Buy,15,55.00,825.00,0.00,TestCorp
2024-04-05,Buy,5,58.00,290.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Gesamt investiert: 500 + 825 + 290 = 1615
        assert analyzer.analysis_results['total_invested'] == 1615.00

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_calculates_total_withdrawn(self, temp_csv_file):
        """
        Test Berechnung der Gesamt-Entnahmen

        Alle Sell-Transaktionen aufsummiert
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,25,50.00,1250.00,0.00,TestCorp
2024-02-15,Sell,8,60.00,480.00,0.00,TestCorp
2024-03-15,Sell,10,65.00,650.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Gesamt entnommen: 480 + 650 = 1130
        assert analyzer.analysis_results['total_withdrawn'] == 1130.00

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_calculates_total_taxes(self, temp_csv_file):
        """
        Test Berechnung der Gesamt-Steuern

        Alle Tax-Einträge aus Verkäufen aufsummiert
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,25,50.00,1250.00,0.00,TestCorp
2024-02-15,Sell,8,60.00,480.00,12.50,TestCorp
2024-03-15,Sell,10,65.00,650.00,25.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Gesamt Steuern: 12.50 + 25.00 = 37.50
        assert analyzer.analysis_results['total_taxes'] == 37.50

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_calculates_net_cashflow(self, temp_csv_file):
        """
        Test Berechnung des Netto-Cashflows

        Net Cashflow = Total Withdrawn - Total Invested
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-15,Sell,8,60.00,480.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Net Cashflow: 480 (withdrawn) - 500 (invested) = -20
        assert analyzer.analysis_results['net_cashflow'] == -20.00

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_calculates_total_return_percentage(self, temp_csv_file):
        """
        Test Berechnung der Gesamt-Rendite in Prozent

        Total Return % = (Total Gains / Total Invested) * 100
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-15,Sell,10,60.00,600.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Total Invested: 500
        # Total Gains: 100
        # Return %: (100 / 500) * 100 = 20%
        assert analyzer.analysis_results['total_return_pct'] == 20.0

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_calculates_total_gains_with_unrealized(self, temp_csv_file):
        """
        Test Berechnung der Gesamt-Gewinne (realisiert + unrealisiert)

        Total Gains = Realized Gains + Unrealized Gains
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,20,50.00,1000.00,0.00,TestCorp
2024-02-15,Sell,10,60.00,600.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file), current_price=70.0)

        # Realized Gains: (10 * 60) - (10 * 50) = 100
        # Unrealized Gains: (10 * 70) - (10 * 50) = 200
        # Total Gains: 100 + 200 = 300
        assert analyzer.analysis_results['total_gains'] == 300.00

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_calculates_remaining_shares_count(self, temp_csv_file):
        """Test Berechnung der verbleibenden Aktienanzahl"""
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,25,50.00,1250.00,0.00,TestCorp
2024-02-15,Sell,8,60.00,480.00,0.00,TestCorp
2024-03-15,Sell,10,65.00,650.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Verbleibende Aktien: 25 - 8 - 10 = 7
        assert analyzer.analysis_results['remaining_shares'] == 7

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_calculates_remaining_value(self, temp_csv_file):
        """
        Test Berechnung des aktuellen Wertes der verbleibenden Aktien

        Current Value = Remaining Shares * Current Price
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-15,Sell,3,60.00,180.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file), current_price=75.0)

        # Verbleibend: 7 Aktien
        # Current Value: 7 * 75 = 525
        assert analyzer.analysis_results['current_value'] == 525.00

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_calculates_cost_basis_of_remaining_shares(self, temp_csv_file):
        """
        Test Berechnung der Kostenbasis der verbleibenden Aktien

        Dies ist wichtig für die Berechnung unrealisierter Gewinne
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-20,Buy,15,55.00,825.00,0.00,TestCorp
2024-03-10,Sell,8,60.00,480.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # FIFO: 8 aus erstem Kauf verkauft
        # Verbleibend: 2 @ 50 + 15 @ 55 = 100 + 825 = 925
        assert analyzer.analysis_results['remaining_cost_basis'] == 925.00


class TestSummaryStatsEdgeCases:
    """Tests für Sonderfälle in der Summary Stats Berechnung"""

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_only_buys_no_sells(self, temp_csv_file):
        """Test Statistiken wenn nur Käufe, keine Verkäufe vorhanden sind"""
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-20,Buy,15,55.00,825.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        assert analyzer.analysis_results['total_invested'] == 1325.00
        assert analyzer.analysis_results['total_withdrawn'] == 0.00
        assert analyzer.analysis_results['total_realized_gains'] == 0.00
        assert analyzer.analysis_results['remaining_shares'] == 25

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_complete_liquidation_stats(self, temp_csv_file):
        """Test Statistiken bei vollständiger Liquidation"""
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-15,Sell,10,60.00,600.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        assert analyzer.analysis_results['remaining_shares'] == 0
        assert analyzer.analysis_results['remaining_cost_basis'] == 0.00
        # Unrealized gains sollten 0 sein bei vollständiger Liquidation
        if 'unrealized_gains' in analyzer.analysis_results:
            assert analyzer.analysis_results['unrealized_gains'] == 0.00

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_stats_without_current_price(self, temp_csv_file):
        """
        Test dass Statistiken auch ohne current_price berechnet werden

        Unrealized gains sollten dann 0 oder None sein
        """
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-15,Sell,5,60.00,300.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))  # Kein current_price

        # Sollte trotzdem andere Stats berechnen
        assert analyzer.analysis_results['total_invested'] == 500.00
        assert analyzer.analysis_results['total_realized_gains'] == 50.00

        # Unrealized gains sollten 0 oder None sein
        if 'unrealized_gains' in analyzer.analysis_results:
            assert analyzer.analysis_results['unrealized_gains'] in [0.00, None]

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_negative_total_return(self, temp_csv_file):
        """Test dass negative Rendite korrekt berechnet wird"""
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,100.00,1000.00,0.00,TestCorp
2024-02-15,Sell,10,80.00,800.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Total Invested: 1000
        # Total Realized Gains: -200
        # Return %: (-200 / 1000) * 100 = -20%
        assert analyzer.analysis_results['total_return_pct'] == -20.0


class TestCompleteAnalysisResults:
    """Tests für vollständige Analyse-Ergebnisse"""

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_analysis_results_contains_all_required_keys(self, temp_csv_file, simple_csv_content):
        """Test dass analysis_results alle erforderlichen Keys enthält"""
        temp_csv_file.write_text(simple_csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file), current_price=70.0)

        required_keys = [
            'total_invested',
            'total_withdrawn',
            'total_realized_gains',
            'total_taxes',
            'net_realized_gains',
            'total_gains',
            'net_cashflow',
            'total_return_pct'
        ]

        for key in required_keys:
            assert key in analyzer.analysis_results, f"Missing key: {key}"

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_expected_results_for_simple_scenario(self, temp_csv_file, simple_csv_content, expected_analysis_results_simple):
        """
        Test dass die erwarteten Werte für ein einfaches Szenario korrekt berechnet werden

        Verwendet die Fixtures aus conftest.py
        """
        temp_csv_file.write_text(simple_csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        for key, expected_value in expected_analysis_results_simple.items():
            if key in analyzer.analysis_results:
                actual_value = analyzer.analysis_results[key]
                assert actual_value == pytest.approx(expected_value, rel=1e-2), \
                    f"Mismatch for {key}: expected {expected_value}, got {actual_value}"

    @pytest.mark.xfail(reason="Summary stats calculation not yet implemented", strict=False)
    def test_analysis_results_use_correct_data_types(self, temp_csv_file, simple_csv_content):
        """Test dass alle Werte im analysis_results Dict den richtigen Typ haben"""
        temp_csv_file.write_text(simple_csv_content)
        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file), current_price=70.0)

        # Alle Finanzwerte sollten floats sein
        financial_keys = [
            'total_invested', 'total_withdrawn', 'total_realized_gains',
            'total_taxes', 'net_realized_gains', 'total_gains', 'net_cashflow'
        ]

        for key in financial_keys:
            if key in analyzer.analysis_results:
                assert isinstance(analyzer.analysis_results[key], (float, int)), \
                    f"{key} should be numeric, got {type(analyzer.analysis_results[key])}"

        # Return percentage sollte auch numeric sein
        if 'total_return_pct' in analyzer.analysis_results:
            assert isinstance(analyzer.analysis_results['total_return_pct'], (float, int))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
