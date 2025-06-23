import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import time

class ValorantIntelligenceEngine:
    """Advanced account analysis and data intelligence for Valorant accounts"""
    
    def __init__(self):
        self.skin_database = self._initialize_skin_database()
        self.rank_values = {
            'Iron 1': 1, 'Iron 2': 2, 'Iron 3': 3,
            'Bronze 1': 4, 'Bronze 2': 5, 'Bronze 3': 6,
            'Silver 1': 7, 'Silver 2': 8, 'Silver 3': 9,
            'Gold 1': 10, 'Gold 2': 11, 'Gold 3': 12,
            'Platinum 1': 13, 'Platinum 2': 14, 'Platinum 3': 15,
            'Diamond 1': 16, 'Diamond 2': 17, 'Diamond 3': 18,
            'Ascendant 1': 19, 'Ascendant 2': 20, 'Ascendant 3': 21,
            'Immortal 1': 22, 'Immortal 2': 23, 'Immortal 3': 24,
            'Radiant': 25
        }
    
    def _initialize_skin_database(self) -> Dict:
        """Initialize comprehensive skin database with market values"""
        return {
            # Knife Skins (High Value)
            'Prime//2.0 Karambit': {'value': 175, 'tier': 'Ultra', 'type': 'knife'},
            'Reaver Karambit': {'value': 175, 'tier': 'Ultra', 'type': 'knife'},
            'Sovereign Sword': {'value': 175, 'tier': 'Ultra', 'type': 'knife'},
            'Glitchpop Dagger': {'value': 175, 'tier': 'Ultra', 'type': 'knife'},
            'Elderflame Dagger': {'value': 175, 'tier': 'Ultra', 'type': 'knife'},
            'Singularity Knife': {'value': 175, 'tier': 'Ultra', 'type': 'knife'},
            'RGX 11z Pro Blade': {'value': 175, 'tier': 'Ultra', 'type': 'knife'},
            'Champions 2021 Karambit': {'value': 300, 'tier': 'Exclusive', 'type': 'knife'},
            'Champions 2022 Butterfly Knife': {'value': 275, 'tier': 'Exclusive', 'type': 'knife'},
            
            # Premium Rifle Skins
            'Prime Vandal': {'value': 87, 'tier': 'Premium', 'type': 'rifle'},
            'Elderflame Vandal': {'value': 87, 'tier': 'Premium', 'type': 'rifle'},
            'Reaver Vandal': {'value': 87, 'tier': 'Premium', 'type': 'rifle'},
            'Prime Phantom': {'value': 87, 'tier': 'Premium', 'type': 'rifle'},
            'Ion Phantom': {'value': 87, 'tier': 'Premium', 'type': 'rifle'},
            'Oni Phantom': {'value': 87, 'tier': 'Premium', 'type': 'rifle'},
            'Glitchpop Vandal': {'value': 87, 'tier': 'Premium', 'type': 'rifle'},
            'Spectrum Phantom': {'value': 87, 'tier': 'Premium', 'type': 'rifle'},
            
            # Operator Skins
            'Prime Operator': {'value': 87, 'tier': 'Premium', 'type': 'sniper'},
            'Elderflame Operator': {'value': 87, 'tier': 'Premium', 'type': 'sniper'},
            'Ion Operator': {'value': 87, 'tier': 'Premium', 'type': 'sniper'},
            'Reaver Operator': {'value': 87, 'tier': 'Premium', 'type': 'sniper'},
            
            # Exclusive/Limited Skins
            'Champions 2021 Vandal': {'value': 150, 'tier': 'Exclusive', 'type': 'rifle'},
            'Champions 2022 Phantom': {'value': 125, 'tier': 'Exclusive', 'type': 'rifle'},
            'Give Back Bundle': {'value': 200, 'tier': 'Exclusive', 'type': 'bundle'},
        }
    
    def analyze_account_response(self, response_data: Dict, username: str) -> Dict:
        """Analyze Riot API response to extract account intelligence"""
        intelligence = {
            'username': username,
            'rank': None,
            'region': None,
            'level': None,
            'competitive_rank': None,
            'rr_points': None,
            'peak_rank': None,
            'skins_count': 0,
            'knife_skins': [],
            'premium_skins': [],
            'battle_pass_level': None,
            'valorant_points': 0,
            'estimated_value': 0.0,
            'last_match_date': None,
            'total_matches': 0,
            'win_rate': 0.0,
            'hours_played': 0.0,
            'two_factor_enabled': False,
            'phone_verified': False,
            'email_verified': False,
            'creation_date': None,
            'security_score': 0
        }
        
        try:
            # Extract account level and region
            if 'account' in response_data:
                account_data = response_data['account']
                intelligence['level'] = account_data.get('account_level', 0)
                intelligence['region'] = account_data.get('region', 'Unknown')
                intelligence['creation_date'] = account_data.get('created_at')
                
            # Extract competitive data
            if 'competitive' in response_data:
                comp_data = response_data['competitive']
                intelligence['competitive_rank'] = comp_data.get('current_rank')
                intelligence['rr_points'] = comp_data.get('ranking_in_tier', 0)
                intelligence['peak_rank'] = comp_data.get('peak_rank')
                
            # Extract match history
            if 'matches' in response_data:
                matches = response_data['matches']
                intelligence['total_matches'] = len(matches)
                if matches:
                    wins = sum(1 for match in matches if match.get('won', False))
                    intelligence['win_rate'] = (wins / len(matches)) * 100
                    intelligence['last_match_date'] = matches[0].get('match_start_time')
                    
                    # Calculate hours played (approximate)
                    total_rounds = sum(match.get('rounds_played', 0) for match in matches)
                    intelligence['hours_played'] = (total_rounds * 2.5) / 60  # ~2.5 min per round
            
            # Extract inventory/skins data
            if 'inventory' in response_data:
                inventory = response_data['inventory']
                self._analyze_inventory(inventory, intelligence)
            
            # Extract security settings
            if 'security' in response_data:
                security = response_data['security']
                intelligence['two_factor_enabled'] = security.get('mfa_enabled', False)
                intelligence['phone_verified'] = security.get('phone_verified', False)
                intelligence['email_verified'] = security.get('email_verified', False)
                
            # Calculate security score
            intelligence['security_score'] = self._calculate_security_score(intelligence)
            
            # Calculate estimated account value
            intelligence['estimated_value'] = self._calculate_account_value(intelligence)
            
        except Exception as e:
            print(f"Error analyzing account data: {e}")
            
        return intelligence
    
    def _analyze_inventory(self, inventory: Dict, intelligence: Dict):
        """Analyze account inventory for valuable items"""
        skins = inventory.get('skins', [])
        intelligence['skins_count'] = len(skins)
        
        knife_skins = []
        premium_skins = []
        total_skin_value = 0
        
        for skin in skins:
            skin_name = skin.get('display_name', '')
            
            # Check if it's a known valuable skin
            if skin_name in self.skin_database:
                skin_data = self.skin_database[skin_name]
                total_skin_value += skin_data['value']
                
                if skin_data['type'] == 'knife':
                    knife_skins.append({
                        'name': skin_name,
                        'value': skin_data['value'],
                        'tier': skin_data['tier']
                    })
                elif skin_data['tier'] in ['Premium', 'Ultra', 'Exclusive']:
                    premium_skins.append({
                        'name': skin_name,
                        'value': skin_data['value'],
                        'tier': skin_data['tier']
                    })
        
        intelligence['knife_skins'] = knife_skins
        intelligence['premium_skins'] = premium_skins
        intelligence['inventory_value'] = total_skin_value
        
        # Extract battle pass info
        if 'battle_pass' in inventory:
            bp_data = inventory['battle_pass']
            intelligence['battle_pass_level'] = bp_data.get('level', 0)
            
        # Extract currency
        if 'currency' in inventory:
            currency = inventory['currency']
            intelligence['valorant_points'] = currency.get('valorant_points', 0)
    
    def _calculate_security_score(self, intelligence: Dict) -> int:
        """Calculate account security score (0-100)"""
        score = 0
        
        if intelligence['two_factor_enabled']:
            score += 40
        if intelligence['phone_verified']:
            score += 25
        if intelligence['email_verified']:
            score += 15
        if intelligence['level'] and intelligence['level'] > 20:
            score += 10  # Higher level = more established account
        if intelligence['total_matches'] > 50:
            score += 10  # More matches = more established
            
        return min(score, 100)
    
    def _calculate_account_value(self, intelligence: Dict) -> float:
        """Calculate estimated account value in USD"""
        value = 0.0
        
        # Base value for level
        if intelligence['level']:
            value += intelligence['level'] * 0.5
        
        # Rank value
        if intelligence['competitive_rank']:
            rank_multiplier = self.rank_values.get(intelligence['competitive_rank'], 1)
            value += rank_multiplier * 2.0
        
        # Inventory value
        value += intelligence.get('inventory_value', 0)
        
        # VP value (approximate conversion)
        if intelligence['valorant_points']:
            value += intelligence['valorant_points'] * 0.01  # ~$1 per 100 VP
        
        # Premium multipliers
        if intelligence['knife_skins']:
            value *= 1.5  # Knife skins add significant value
        
        if intelligence['security_score'] > 80:
            value *= 1.2  # Secure accounts are worth more
            
        if intelligence['hours_played'] > 100:
            value *= 1.1  # Well-played accounts
            
        return round(value, 2)
    
    def categorize_account_value(self, estimated_value: float) -> str:
        """Categorize account by value tier"""
        if estimated_value >= 500:
            return "Ultra High Value"
        elif estimated_value >= 200:
            return "High Value"
        elif estimated_value >= 100:
            return "Medium Value"
        elif estimated_value >= 50:
            return "Low Value"
        else:
            return "Basic"
    
    def generate_account_summary(self, intelligence: Dict) -> str:
        """Generate a human-readable account summary"""
        summary = []
        
        if intelligence['competitive_rank']:
            summary.append(f"Rank: {intelligence['competitive_rank']}")
            
        if intelligence['level']:
            summary.append(f"Level {intelligence['level']}")
            
        if intelligence['knife_skins']:
            knife_count = len(intelligence['knife_skins'])
            summary.append(f"{knife_count} knife skin{'s' if knife_count > 1 else ''}")
            
        if intelligence['premium_skins']:
            premium_count = len(intelligence['premium_skins'])
            summary.append(f"{premium_count} premium skin{'s' if premium_count > 1 else ''}")
            
        value_category = self.categorize_account_value(intelligence['estimated_value'])
        summary.append(f"${intelligence['estimated_value']} ({value_category})")
        
        return " | ".join(summary) if summary else "Basic Account"