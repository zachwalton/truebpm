# True BPM

[![](https://travis-ci.org/zachwalton/truebpm.svg?branch=master)](https://travis-ci.org/zachwalton/truebpm/builds)

https://truebpm.dance

Pick a preferred read speed and select a song. You'll get a breakdown of BPM duration:

![](/images/demo.png)

# Contributing

## Setup

### Requirements

- NodeJS 8+
- Yarn 1.22.4
- Python 3.6.11
  - Using [pyenv](https://github.com/pyenv/pyenv) is probably the easiest way to do this.

Set up a virtual env and install dependencies:

```
pyenv install (This'll install 3.6.11 if you don't have it already)
pyenv virtualenv truebpm
pyenv activate truebpm
```

To serve the API + frontend, `./serve.sh`

This will serve the API + frontend on `http://127.0.0.1:5000`. If you just want to work on the frontend, you may want to use yarn to get the benefits of live reloading:

```
cd frontend/ && yarn run start
```

## Adding Simfiles

Simfiles live in the `simfiles/` directory, and the filenames are formatted as `<title> - <artist>`. To add a simfile, just run `./convert.py </path/to/simfile.sm>` and it will rename it for you. Drop it in the `simfiles/` directory and submit a PR.

CI will test to make sure that the simfile is valid. If pull request verification fails, check the build logs.
