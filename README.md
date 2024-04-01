# BoM radar grabber

This is a simple Python tool for periodically scraping radar images from the [Australian Bureau of Meteorology (BoM)](http://www.bom.gov.au/).

**WARNING:** This tool is not made by, or condoned by, the BoM, and usage of this tool is fully at your own risk. Despite that, it has been written to minimise traffic to BoM's website, so it should be fine in most cases.

## Installation

Clone this GitHub repository:

```
git clone https://github.com/itsmevjnk/BoM-Radar-Grabber
```

This program requires Python 3 with the `requests` module installed. To install Python, refer to your distribution's tutorial/package manager or [the Python website](https://www.python.org/). Once it has been installed, the `requests` module can be installed using `pip`:

```
python3 -m pip install requests
```

## Usage

To show the list of available commands, use the `-h` argument:

```
python3 bomgrab.py -h
```

The image to be scraped can be specified using either its URL or its source ID coded in the `sources.json` file (which can also be found using the `-sid` argument). For example, this command below scrapes the 64 km radar image from the Melbourne weather radar station:

```
python3 bomgrab.py -id vic/melbourne/64
```

**NOTE:** The `sources.json` file as of now only contains the national radar image source, as well as sources from the Melbourne station. Refer to the **Contributing** section if you are interested in adding more stations to the list.


## Contributing

Contributions to this project through pull requests and issues are welcome.

## License

This software is licensed under the MIT license; additional information can be found in the repository's `LICENSE.txt` file.