from fasthtml.common import *
from dataclasses import dataclass
from typing import Optional
import decimal
from decimal import Decimal

@dataclass
class LoanParams:
    emprunt: Decimal
    annual_rate: Decimal
    years: int
    
    @property
    def monthly_rate(self) -> Decimal:
        return self.annual_rate / Decimal('100') / Decimal('12')
    
    @property
    def total_months(self) -> int:
        return self.years * 12

class LoanCalculator:
    def __init__(self, params: LoanParams):
        self.params = params
        
    def calculate(self) -> tuple[Decimal, Decimal]:
        """Calculate monthly payment and total cost of the loan."""
        tol = Decimal('1E-6')
        
        if abs(self.params.monthly_rate) < tol:
            monthly_payment = self.params.emprunt / self.params.total_months
            total_cost = Decimal('0')
        else:
            rate = self.params.monthly_rate
            months = self.params.total_months
            emprunt = self.params.emprunt
            
            c1 = emprunt * rate / (pow(1 + rate, months) - 1)
            monthly_payment = emprunt * rate + c1
            total_cost = c1 * months * pow(1 + rate, months) - emprunt
            
        return round(monthly_payment, 2), round(total_cost, 2)

app, rt = fast_app()

@rt()
def index():
    return Titled(
        "Calculateur de prêt",
        Article(
            P("Calculez facilement vos mensualités et le coût total de votre emprunt"),
            Form(
                hx_post="/submit",
                hx_target="#result"
            )(
                Input(
                    name='emprunt',
                    placeholder="Montant de l'emprunt en euros",
                    type="number",
                    step="0.01",
                    min="0",
                    required=True
                ),
                Input(
                    name='rate',
                    placeholder="Taux annuel en %",
                    type="number",
                    step="0.01",
                    min="0",
                    required=True
                ),
                Input(
                    name='years',
                    placeholder="Durée de remboursement en années",
                    type="number",
                    min="1",
                    required=True
                ),
                Button("Calculer", type="submit")
            ),
            Div(id="result")
        )
    )

@rt("/submit")
def submit(emprunt: str, rate: str, years: str):
    try:
        loan_params = LoanParams(
            emprunt=Decimal(emprunt),
            annual_rate=Decimal(rate),
            years=int(years)
        )
        
        calculator = LoanCalculator(loan_params)
        monthly_payment, total_cost = calculator.calculate()
        
        return Div(
            Article(
                Header(H3("Résultats du calcul")),
                P(f"Mensualité: {monthly_payment} euros"),
                P(f"Coût total du prêt: {total_cost} euros"),
                P(A('Réinitialisation', href='/')),
            )
        )
        
    except (ValueError, decimal.InvalidOperation) as e:
        return Div(
            P("Erreur: Veuillez vérifier vos données d'entrée.", cls="error-message")
        )

serve()