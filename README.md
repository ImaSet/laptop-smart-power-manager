# LSPM - Laptop Smart Power Manager

The **Laptop Smart Power Manager** is a lightweight tool 
designed to autonomously manage laptop battery 
charge cycles with the help of a _Smart Plug_.

## Description

When we are at home or at work, we may tend to leave our 
laptop plugged in and constantly charging.
The problem of this practice is that it will damage the 
laptop battery prematurely.<br />
To extend the battery life, it is recommended to [unplug 
the charger before the battery reaches 100% and plug it 
in before the battery is completely discharged](
https://www.wired.com/2013/09/laptop-battery/?cid=12494134).
However, constantly keeping an eye on your computer's 
battery level turns out to be difficult in practice.

This is what the **Laptop Smart Power Manager** has to 
offer: it takes care of managing, for you, the charging 
cycles of your laptop in order to optimize its battery 
life.

To achieve this, **LSPM** needs an additional accessory: 
a _Smart Plug_.<br />
The laptop must be plugged into the _Smart Plug_ and both 
must be connected to the same local network:

![Diagram of LSPM](./docs/static/lspm_schema_dark.png#gh-dark-mode-only)
![Diagram of LSPM](./docs/static/lspm_schema_light.png#gh-light-mode-only)

The operating principle is quite simple:

- if the battery level drops below 20%, **LSPM** tells the 
_Smart Plug_ to turn on. The laptop then starts charging.
- if the battery level reaches 100%, **LSPM** tells the 
_Smart Plug_ to turn off. The laptop then stops charging.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Supported devices](#supported-devices)
- [Contributing](#contributing)
- [License](#license)

## Installation

`lspm` can be installed using the package manager 
[pip](https://pip.pypa.io/en/stable/).

```bash
pip install lspm
```

## Configuration

### Prerequisites

Before using **LSPM**, your _Smart Plug_ must be plugged in, 
configured and connected to the same local network as 
your laptop.

To work properly, **LSPM** needs some information 
about the _Smart Plug_:

- IP Address
- Username
- Password

### Command Line Interface

The easiest way is to use the command line tool `lspm`.

For the first use, enter the configuration parameters 
of your _Smart Plug_ using the command `lspm config`:

```bash
$> lspm config
Enter the Smart Plug IP Address:
Enter a new username: 
Enter a new password: 
```

To get the available options for this command, 
run `lspm config --help`.

## Usage

### Command Line Interface

The easiest way is to use the command line tool `lspm`.

To start **LSPM**, run the command `lspm start`:

```bash
$> lspm start
Laptop Smart Power Manager started correctly
To stop it, press CTRL + C (on macOS, Command + .)
```

To stop it, press `CTRL + C` (or `Command + .` 
on _macOS_). Then, the following message 
should show up:

```bash
Laptop Smart Power Manager stopped successfully
```

## Supported devices

### TP-Link

- **Tapo**
  - P100
  - P105 (not tested)
  - P110 (not tested)

## Contributing

Contributions, issues and feature requests are 
always welcome!

## License

Copyright © 2023 [Imanol Setoain](https://github.com/ImaSet).<br />
This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.