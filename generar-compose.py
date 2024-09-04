import sys

ADD_ENV_VARS=False

SERVER_BASE_CONFIG = {
    "container_name": "server",
    "image": "server:latest",
    "entrypoint": "python3 /main.py",
    "networks": ["testing_net"],
    "volumes": ["./server/config.ini:/config/config.ini"]
  }
CLIENT_BASE_CONFIG = {
    "container_name": "client",
    "image": "client:latest",
    "entrypoint": "/client",
    "networks": ["testing_net"],
    "depends_on": ["server"],
    "volumes": ["./client/config.yaml:/config/config.yaml"]
  }

SERVER_CHECKER_CONFIG = {
    "container_name": "server-checker",
    "image": "busybox",
    "networks": ['testing_net'],
    "command": "tail -f /dev/null" 
  }

if ADD_ENV_VARS:
  SERVER_BASE_CONFIG["environment"] = {
      "PYTHONUNBUFFERED": "1",
      "LOGGING_LEVEL": "DEBUG"
  }
  CLIENT_BASE_CONFIG["environment"] = {
      "CLI_LOG_LEVEL": "DEBUG",
    }
def generate_docker_compose(filename, client_amount):
  """
  Generates a Docker Compose file with specified filename and client count.

  Args:
      filename (str): The desired filename for the Docker Compose file.
      client_amount (int): The number of client containers to replicate.
  """
  # Validate inputs
  if not isinstance(filename, str):
    raise ValueError("filename must be a string")
  if not isinstance(client_amount, int) or client_amount <= 0:
    raise ValueError("client_amount must be a positive integer")


  client_config = CLIENT_BASE_CONFIG
  # Create the Docker Compose file content
  content = "name: tp0\n"
  content += "services:\n"
  content += f"  server:\n"
  content += f"{yaml_format(SERVER_BASE_CONFIG)}\n"

  for i in range(1, client_amount + 1):
    client_config["container_name"] = f"client{i}"
    if ADD_ENV_VARS:
      client_config["environment"]["CLI_ID"] = str(i)
    content += f"  client{i}:\n"
    content += f"{yaml_format(client_config)}\n"
    client_config["container_name"] = "client"  # Reset client container name
  
  content += f"  server-checker:\n"
  content += f"{yaml_format(SERVER_CHECKER_CONFIG)}\n"

  content += "networks:\n"
  content += "  testing_net:\n"
  content += "    ipam:\n"
  content += "      driver: default\n"
  content += "      config:\n"
  content += "        - subnet: 172.25.125.0/24\n"

  # Write the content to the file
  with open(filename, "w") as f:
    f.write(content)

  print(f"Docker Compose file generated successfully: {filename}")


def yaml_format(data):
  """
  Formats a dictionary in a YAML-like style for indentation.

  Args:
      data (dict): The dictionary to format.

  Returns:
      str: The formatted string.
  """

  formatted = ""
  for key, value in data.items():
    formatted += f"    {key}: {value}\n"
  return formatted


if __name__ == "__main__":
  try:
    generate_docker_compose(sys.argv[1], int(sys.argv[2]))
  except ValueError as e:
    print(f"Error: {e}")
    sys.exit(1)