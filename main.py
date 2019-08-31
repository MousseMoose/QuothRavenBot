import json
from QuothRaven import QuothRavenDiscordClient

try:
    file = open('config.json')
    configData = json.load(file)
    file.close()
except Exception as e:
    print(e)
    quit()

client = QuothRavenDiscordClient()
client.run(configData["discord"]["token"])









