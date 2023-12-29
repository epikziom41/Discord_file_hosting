import discord
import os
import json
import paramiko
import shutil
import logging
import time
import asyncio

async def download_files(file_id):
    try:
        temp_folder = 'temp'
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect('ip', username='user', password='pass')

        sftp_client = ssh_client.open_sftp()
        sftp_client.get('files.json', os.path.join(temp_folder, 'files.json'))
        sftp_client.close()
        ssh_client.close()

        with open(os.path.join(temp_folder, 'files.json'), 'r') as json_file:
            chunks_info = json.load(json_file)

        if file_id in chunks_info:
            info = chunks_info[file_id]
            combined_file_name = info['file_name']
            combined_file_path = os.path.join(temp_folder, combined_file_name)

            channel_id = channel_id

            total_parts = len(info['parts'])
            downloaded_parts = 0
            start_time = time.time()

            for part in info['parts']:
                file_id = part['message_id']

                channel = client.get_channel(channel_id)
                message = await channel.fetch_message(file_id)

                if len(message.attachments) > 0:
                    attachment = message.attachments[0]
                    file_data = await attachment.read()

                    with open(combined_file_path, 'ab') as combined_file:
                        combined_file.write(file_data)

                    downloaded_parts += 1
                    time_elapsed = time.time() - start_time
                    speed_mb_per_sec = (downloaded_parts * len(file_data) / (1024 * 1024)) / time_elapsed if time_elapsed > 0 else 0

                    print(f"Downloaded {downloaded_parts}/{total_parts} Parts. Average speed: {speed_mb_per_sec:.2f} MB/s.")

            print(f"Linked files for {combined_file_name}.")

            for filename in os.listdir(temp_folder):
                file_path = os.path.join(temp_folder, filename)
                if os.path.isfile(file_path) and filename != combined_file_name:
                    os.remove(file_path)
        else:
            print("The specified file ID does not exist on the server.")

    except Exception as e:
        print(f"An error occurred while downloading the file.: {e}")

if __name__ == "__main__":
    TOKEN = 'discord_bot_token'

    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        try:
            file_id = input("Enter the ID of the file to download: ")
            
            await download_files(file_id)
            
            print ("There is a file in Temp.")
            await asyncio.sleep(5)
            await client.close()

        except Exception as e:
            print(f"An error occured: {e}")

    client.run(TOKEN)