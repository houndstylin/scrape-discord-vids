import requests
import os
import time

def getheaders(token):
    return {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

def getdamessages(headers, channel_id, limit=100):
    url = f'https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def downloadvideo(url, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'wb') as f:
        f.write(response.content)

def sendthestuff(webhook_url, filename):
    with open(filename, 'rb') as f:
        response = requests.post(webhook_url, files={'file': f})
    response.raise_for_status()
    return response.json()

def main():
    token = input("Enter discord token: ")
    channel_id = input("Channel id to scrape vids from: ")
    webhook_url = input("Webhook to send vids to: ")

    headers = getheaders(token)
    
    try:
        messages = getdamessages(headers, channel_id)
        if not messages:
            print("[-] Couldnt find any messages in channel.")
            return

        for message in messages:
            for attachment in message.get('attachments', []):
                if attachment['content_type'].startswith('video'):
                    video_url = attachment['url']
                    filename = attachment['filename']
                    
                    print(f"[+] Downloading: {filename}")
                    downloadvideo(video_url, filename)
                    
                    print(f"[+] Sending: {filename}")
                    try:
                        sendthestuff(webhook_url, filename)
                    except requests.exceptions.RequestException as e:
                        print(f"[-] Error, skipping. ")
                        continue  
                    
                    os.remove(filename)
                    time.sleep(1)  # wait a second to avoid ratelimitng
                    
        print("Done!")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
