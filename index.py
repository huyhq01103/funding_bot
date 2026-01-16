import requests
import json

def get_top_10_negative_funding():
    url = 'https://fapi.binance.com/fapi/v1/premiumIndex'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Filter for negative funding rates
        negative_funding = [
            item for item in data 
            if 'lastFundingRate' in item and float(item['lastFundingRate']) < 0
        ]
        
        # Sort by funding rate ascending (most negative first)
        sorted_negative = sorted(
            negative_funding, 
            key=lambda x: float(x['lastFundingRate'])
        )
        
        # Get top 10
        top_10 = sorted_negative[:10]
        
        # Print results
        print("Top 10 coins with the highest negative funding rates:")
        for i, item in enumerate(top_10, 1):
            symbol = item['symbol']
            rate = float(item['lastFundingRate']) * 100
            print(f"{symbol}: {rate:.4f}%")
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    get_top_10_negative_funding()
