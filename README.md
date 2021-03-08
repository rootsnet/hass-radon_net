# hass-radon_net
Home Assistant integration for Radon-Net.

## Installation

### Step 1: Install Custom Components

### Step 2: Configure

Example configuration.yaml entry:

```yaml
sensor:
  - platform: radon_net
    name: Radon Net Sensor
    username: <your email for radon-net.com>
    password: <your password for radon-net.com>
    measurement: picocuries
```

|               | Required |     Default      |        Options          |
| ------------- |:--------:|:----------------:|:-----------------------:|
| name          |     X    | Radon Net Sensor |                         |
| username      |     O    |                  |                         |
| password      |     O    |                  |                         |
| measurement   |     X    | picocuries       | picocuries or bequerels |
