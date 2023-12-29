import http.server
import socketserver
import threading
import paramiko
import json
import time

# Path to the local list.json file
local_list_file_path = 'list.json'

# Function to update the list.json file based on data from files.json on the SFTP server
def update_list_file(local_list_file_path):
    try:
        hostname = 'ip'
        port = 22
        username = 'user'
        password = 'pass'

        transport = paramiko.Transport((hostname, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        remote_file_path = 'files.json'
        # Fetch data from files.json on the SFTP server
        with sftp.open(remote_file_path) as remote_file:
            data = json.load(remote_file)

        # Read existing data from list.json
        try:
            with open(local_list_file_path, 'r') as list_file:
                existing_data = json.load(list_file)
            if not isinstance(existing_data, list):
                raise ValueError("Invalid data format in list.json file. Expected a list.")
        except FileNotFoundError:
            existing_data = []

        # Check for new IDs and File Names and update the list
        if isinstance(existing_data, list):  # Additional check if existing_data is a list
            for key, value in data.items():
                file_name = value.get('file_name')
                part_id = value.get('parts')[0].get('id') if 'parts' in value and len(value.get('parts')) > 0 else None
                if file_name and part_id and not any(d['file_name'] == file_name and d['id'] == part_id for d in existing_data):
                    existing_data.append({'file_name': file_name, 'id': part_id})
        else:
            print("Failed to load data from list.json. Creating a new list.")

        # Write updated data to the list.json file
        with open(local_list_file_path, 'w') as list_file:
            json.dump(existing_data, list_file, indent=2)
            print("Updated list.json file")

        sftp.close()
        transport.close()

    except Exception as e:
        print(f"Error updating list.json file: {e}")

# Function handling list updates in a loop every 10 minutes
def update_loop(local_list_file_path):
    while True:
        try:
            # Call function to update the list.json file locally
            update_list_file(local_list_file_path)
        except Exception as e:
            print(f"Error during update: {e}")

        time.sleep(600)  # Waiting time - 10 minutes

# Start updating in a separate thread
update_thread = threading.Thread(target=update_loop, args=(local_list_file_path,))
update_thread.daemon = True
update_thread.start()

# Function handling static files: index.html, style.css, script.js, list.json
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        http.server.SimpleHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        if self.path in ['/', '/index.html', '/style.css', '/script.js', '/list.json']:
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 - Not Found')

# Hosting the website on port 3000
Handler = MyHttpRequestHandler
with socketserver.TCPServer(("", 3000), Handler) as httpd:
    print("Serving at port 3000")
    httpd.serve_forever()
