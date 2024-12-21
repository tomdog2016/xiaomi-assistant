import requests
import json
import time
from urllib.parse import urlencode

class XiaomiAuth:
    def __init__(self):
        # OAuth endpoints
        self.auth_host = "https://account.xiaomi.com"
        self.token_host = "https://api.xiaoai.mi.com"
        
        # Your application credentials (need to be filled)
        self.client_id = "YOUR_CLIENT_ID"
        self.client_secret = "YOUR_CLIENT_SECRET"
        self.redirect_uri = "YOUR_REDIRECT_URI"
        
        # Required scopes
        self.scopes = [
            "device_control",
            "device_query",
            "device_status"
        ]
    
    def get_authorization_url(self):
        """Get the authorization URL for user to login"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(self.scopes)
        }
        
        auth_url = f"{self.auth_host}/oauth2/authorize?{urlencode(params)}"
        return auth_url
    
    def get_token(self, auth_code):
        """Exchange authorization code for access token"""
        token_url = f"{self.token_host}/oauth2/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            return {
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('expires_in')
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting token: {e}")
            return None
    
    def refresh_token(self, refresh_token):
        """Refresh an expired access token"""
        token_url = f"{self.token_host}/oauth2/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            return {
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('expires_in')
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error refreshing token: {e}")
            return None
    
    def get_device_token(self, access_token, device_id):
        """Get device-specific token using access token"""
        device_url = f"{self.token_host}/device/token"
        
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        params = {
            'device_id': device_id
        }
        
        try:
            response = requests.get(device_url, headers=headers, params=params)
            response.raise_for_status()
            
            device_data = response.json()
            return device_data.get('token')
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting device token: {e}")
            return None

def main():
    auth = XiaomiAuth()
    
    # Step 1: Get authorization URL
    auth_url = auth.get_authorization_url()
    print(f"\nPlease visit this URL to authorize the application:")
    print(auth_url)
    
    # Step 2: Get authorization code from user
    auth_code = input("\nEnter the authorization code from the redirect URL: ")
    
    # Step 3: Exchange code for tokens
    token_data = auth.get_token(auth_code)
    if not token_data:
        print("Failed to get access token")
        return
    
    print("\nAccess Token obtained successfully!")
    print(f"Access Token: {token_data['access_token']}")
    print(f"Refresh Token: {token_data['refresh_token']}")
    print(f"Expires in: {token_data['expires_in']} seconds")
    
    # Step 4: Get device token
    device_id = "08f83588"  # Our discovered device ID
    device_token = auth.get_device_token(token_data['access_token'], device_id)
    
    if device_token:
        print(f"\nDevice Token obtained successfully!")
        print(f"Device Token: {device_token}")
    else:
        print("\nFailed to get device token")

if __name__ == "__main__":
    main()
