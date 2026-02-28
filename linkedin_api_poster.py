#!/usr/bin/env python3
"""
LinkedIn API Poster using official LinkedIn API instead of browser automation
"""
import os
import requests
import json
from datetime import datetime
from urllib.parse import urlencode

class LinkedInAPIPoster:
    def __init__(self):
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI')
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')

        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("LinkedIn API credentials not properly set in environment variables")

    def get_authorization_url(self):
        """Generate authorization URL for OAuth 2.0"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'w_member_social r_liteprofile r_emailaddress w_organization_social'
        }

        auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
        return auth_url

    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token"""
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(token_url, data=data, headers=headers)

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            # Save the access token to environment for future use
            os.environ['LINKEDIN_ACCESS_TOKEN'] = self.access_token
            print(f"Access token set: {self.access_token[:20]}...")
            return self.access_token
        else:
            raise Exception(f"Failed to get access token: {response.text}")

    def refresh_access_token(self, refresh_token):
        """Refresh the access token using refresh token"""
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(token_url, data=data, headers=headers)

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            return self.access_token
        else:
            raise Exception(f"Failed to refresh access token: {response.text}")

    def get_user_profile(self):
        """Get current user's LinkedIn profile"""
        if not self.access_token:
            raise Exception("No access token available. Authorize first.")

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        response = requests.get(
            'https://api.linkedin.com/v2/me',
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get user profile: {response.text}")

    def post_text_share(self, text, visibility='PUBLIC'):
        """Post a text share to LinkedIn"""
        if not self.access_token:
            raise Exception("No access token available. Authorize first.")

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        # Get the user's profile to get their URN
        profile = self.get_user_profile()
        author_urn = profile.get('id')

        post_data = {
            "author": f"urn:li:person:{author_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }

        response = requests.post(
            'https://api.linkedin.com/v2/ugcPosts',
            headers=headers,
            json=post_data
        )

        if response.status_code == 201:
            result = response.json()
            print(f"✅ LinkedIn post created successfully!")
            print(f"Post ID: {result.get('id')}")
            return result
        else:
            raise Exception(f"Failed to create LinkedIn post: {response.text}")

    def post_article_share(self, title, description, url, text="", visibility='PUBLIC'):
        """Post an article share to LinkedIn"""
        if not self.access_token:
            raise Exception("No access token available. Authorize first.")

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        # Get the user's profile to get their URN
        profile = self.get_user_profile()
        author_urn = profile.get('id')

        post_data = {
            "author": f"urn:li:person:{author_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": description
                            },
                            "originalUrl": url,
                            "title": {
                                "text": title
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }

        response = requests.post(
            'https://api.linkedin.com/v2/ugcPosts',
            headers=headers,
            json=post_data
        )

        if response.status_code == 201:
            result = response.json()
            print(f"✅ LinkedIn article post created successfully!")
            print(f"Post ID: {result.get('id')}")
            return result
        else:
            raise Exception(f"Failed to create LinkedIn article post: {response.text}")

def main():
    print("LinkedIn API Poster")
    print("=" * 50)

    try:
        poster = LinkedInAPIPoster()

        if not os.getenv('LINKEDIN_ACCESS_TOKEN'):
            print("\n⚠️  No access token found. You need to authorize the app first.")
            print("\nTo authorize:")
            print(f"1. Visit this URL: {poster.get_authorization_url()}")
            print("2. Log in to LinkedIn and authorize the app")
            print("3. Copy the 'code' parameter from the redirect URL")
            print("4. Run this script with the code: python linkedin_api_poster.py --code <your_code>")
            return

        # Example business post content
        business_content = """🚀 Transform Your Business with AI Automation

In today's fast-paced market, businesses that leverage AI automation are seeing 85-90% cost reductions compared to traditional human resources while maintaining consistent, predictable performance.

Key business transformations:
• 24/7 automated operations without breaks
• Significant cost savings with AI employees
• Consistent quality and performance
• Scalable solutions that grow with your business

The future of business is autonomous. Companies that embrace AI-powered automation today will dominate their markets tomorrow. Don't get left behind - start your automation journey now!

Ready to revolutionize your business operations?

#BusinessAutomation #ArtificialIntelligence #DigitalTransformation #BusinessGrowth #Innovation #FutureOfWork #AI #Entrepreneurship"""

        print("Attempting to create LinkedIn post...")
        result = poster.post_text_share(business_content)
        print("✅ LinkedIn post created successfully via API!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()