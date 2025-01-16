import os
import subprocess
import sys
import urllib.request
import requests

# Define constants
MINECRAFT_JAR = "server.jar"
DOWNLOAD_URL = "https://piston-data.mojang.com/v1/objects/4707d00eb834b446575d89a61a11b5d548d8c001/server.jar"
DESKTOP_DIR = os.path.expanduser("~/Desktop")
INSTALL_DIR = os.path.join(DESKTOP_DIR, "Minecraft Server")
EULA_FILE = os.path.join(INSTALL_DIR, "eula.txt")
SERVER_PROPERTIES_FILE = os.path.join(INSTALL_DIR, "server.properties")

# Function to check if Java is installed
def check_java():
    print("Checking for Java installation...")
    try:
        result = subprocess.run(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result.check_returncode()
        print("Java is installed.")
    except subprocess.CalledProcessError:
        print("Error: Java is not installed. Please install Java (17 or higher) and try again.")
        sys.exit(1)

# Function to prompt the user for RAM allocation
def prompt_ram_allocation():
    while True:
        try:
            ram = input("How much RAM would you like to allocate to the server? (e.g., 2G, 4G): ").strip()
            # Validate the RAM format (e.g., 2G, 4G, 1G)
            if ram[-1] in ['G', 'g'] and ram[:-1].isdigit():
                print(f"Allocating {ram} of RAM to the server.")
                return ram
            else:
                print("Invalid RAM input. Please enter a value like '2G' or '4G'.")
        except ValueError:
            print("Invalid input. Please enter a valid RAM value (e.g., 2G, 4G).")

# Function to download the Minecraft server JAR into the Minecraft Server directory
def download_server():
    print("Downloading Minecraft server...")
    try:
        with urllib.request.urlopen(DOWNLOAD_URL) as response:
            with open(os.path.join(INSTALL_DIR, MINECRAFT_JAR), 'wb') as out_file:
                out_file.write(response.read())
        print("Minecraft server downloaded successfully.")
    except Exception as e:
        print(f"Error: Failed to download Minecraft server. {e}")
        sys.exit(1)

# Function to create the Minecraft server directory on the Desktop
def setup_directory():
    print("Creating the Minecraft server directory on the Desktop...")
    if not os.path.exists(INSTALL_DIR):
        os.makedirs(INSTALL_DIR)

# Function to run the server and generate necessary files
def run_server(ram):
    print(f"Starting the Minecraft server for the first time to generate required files with {ram} of RAM...")
    try:
        subprocess.run(["java", f"-Xmx{ram}", f"-Xms{ram}", "-jar", MINECRAFT_JAR, "nogui"], check=True, cwd=INSTALL_DIR)
    except subprocess.CalledProcessError:
        print("Error: Failed to start the Minecraft server.")
        sys.exit(1)

# Function to stop the Minecraft server
def stop_server():
    print("Stopping the Minecraft server...")
    try:
        subprocess.run(["java", "-Xmx1G", "-Xms1G", "-jar", MINECRAFT_JAR, "nogui", "stop"], check=True, cwd=INSTALL_DIR)
    except subprocess.CalledProcessError:
        print("Error: Failed to stop the Minecraft server.")
        sys.exit(1)

# Function to accept the EULA
def accept_eula():
    print("Accepting the EULA...")
    if os.path.exists(EULA_FILE):
        with open(EULA_FILE, "r") as file:
            eula_content = file.read()
        if "eula=false" in eula_content:
            eula_content = eula_content.replace("eula=false", "eula=true")
            with open(EULA_FILE, "w") as file:
                file.write(eula_content)
            print("EULA accepted.")
        else:
            print("EULA already accepted.")
    else:
        print("Error: EULA file not found.")
        sys.exit(1)

# Function to create a run.bat file for the user
def create_run_bat(ram):
    bat_file_path = os.path.join(INSTALL_DIR, "run.bat")
    with open(bat_file_path, "w") as bat_file:
        bat_file.write(f'java -Xmx{ram} -Xms{ram} -jar {MINECRAFT_JAR} nogui\n')
    print(f"Created run.bat file at {bat_file_path}. You can edit this file to change memory allocation if needed.")

# Function to prompt user for input
def prompt_exit():
    while True:
        user_input = input("Type 'exit' to quit the script or press Enter to continue: ").strip().lower()
        if user_input == "exit":
            print("Exiting the script.")
            sys.exit(0)

# Main function
def main():
    # Check for Java installation
    check_java()
    
    # Prompt the user for RAM allocation
    ram = prompt_ram_allocation()
    
    # Setup the server directory
    setup_directory()
    
    # Download the Minecraft server into the Minecraft Server directory
    download_server()
    
    # Change to the server directory before running the server
    os.chdir(INSTALL_DIR)
    
    # Run the server to generate necessary files with the allocated RAM
    run_server(ram)
    
    # Accept the EULA and configure properties
    accept_eula()
    
    # Stop the server
    stop_server()
    
    # Restart the server after configuring IP
    print("Restarting Minecraft server with updated server properties...")
    try:
        subprocess.run(["java", f"-Xmx{ram}", f"-Xms{ram}", "-jar", MINECRAFT_JAR, "nogui"], check=True, cwd=INSTALL_DIR)
    except subprocess.CalledProcessError:
        print("Error: Failed to restart the Minecraft server.")
        sys.exit(1)

    # Create the run.bat file for the user
    create_run_bat(ram)
    
    # Instructions for future use
    print("Setup complete! To start your server in the future, run the following command from the Minecraft Server folder:")
    print(f"cd \"{INSTALL_DIR}\" && java -Xmx{ram} -Xms{ram} -jar \"{MINECRAFT_JAR}\" nogui")
    
    # Prompt for exit
    prompt_exit()

# Run the script
if __name__ == "__main__":
    main()