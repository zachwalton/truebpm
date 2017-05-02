# True BPM

![](https://travis-ci.org/zachwalton/truebpm.svg?branch=master)

https://truebpm.dance

Pick a preferred read speed and select a song. You'll get a breakdown of BPM duration:

![](/images/demo.png)

# Contributing

## Setup

You'll need a working node + NPM installation to build the frontend and a working Python + virtualenv installation to work with the API server / simfile parser.

To serve the API + frontend, run:

```
virtualenv venv && source venv/bin/activate
pip install -r requirements.txt -r dev_requirements.txt
cd frontend/ && npm run build && cd -
honcho start
```

This will serve the API + frontend on `http://127.0.0.1:5000`. If you just want to work on the frontend, you may want to use npm to get the benefits of live reloading:

```
cd frontend/ && npm run start
```

## Adding Simfiles

Simfiles live in the `simfiles/` directory, and the filenames are formatted as `<title> - <artist>`. To add a simfile, just run `./convert.py </path/to/simfile.sm>` and it will rename it for you. Drop it in the `simfiles/` directory and submit a PR.
