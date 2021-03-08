# hass-radon_net

Home Assistant integration for Radon-Net. 

This custom component will work with RadonEye Wi-Fi models(eg: RadonEye Plus 2) 

And this was tested by Radon-Net account what have a RadonEye Plus2.

## Installation

### Step 1: Install Custom Component

Copy the radon_net directory into the custom_components folder

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
| ------------- |:--------:|:----------------:| ----------------------- |
| name          |     X    | Radon Net Sensor | As a name you want      |
| username      |     O    |                  |                         |
| password      |     O    |                  |                         |
| measurement   |     X    | picocuries       | picocuries or bequerels |
