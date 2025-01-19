from dataclasses import dataclass
from decimal import Decimal

@dataclass
class UserAsset: 
    asset: str
    free: Decimal
    locked: Decimal = Decimal('0')
    freeze: Decimal = Decimal('0')
    withdrawing: Decimal = Decimal('0')
    btc_valuation: Decimal = Decimal('0')  
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserAsset':
        return cls(
            asset=data['asset'],
            free=Decimal(data['free']),
            locked=Decimal(data.get('locked', '0')),
            freeze=Decimal(data.get('freeze', '0')),
            withdrawing=Decimal(data.get('withdrawing', '0')),
            btc_valuation=Decimal(data.get('btcValuation', '0'))
        )