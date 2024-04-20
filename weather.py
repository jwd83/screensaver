import json

def main():

    # load the settings.json into a settings object
    with open('settings.json') as json_file:
        settings = json.load(json_file)

if __name__ == '__main__':
    main()
    
