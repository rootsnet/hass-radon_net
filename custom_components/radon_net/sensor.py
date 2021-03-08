"""Platform for sensor integration."""
import requests
import json
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from datetime import timedelta
from homeassistant.util import Throttle
from homeassistant.core import CoreState, HomeAssistant
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.const import (CONF_NAME, CONF_USERNAME, CONF_PASSWORD)
from _ast import Attribute

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)

ATTR_SN = 'SN'
ATTR_LOCATION = 'Location'
ATTR_DT = 'Date Time'
ATTR_TIMEZONE = 'TimeZone'
ATTR_RADON_BQ = 'Radon Value (Bq/㎥)'
ATTR_RADON_PCI = 'Radon Value (pCi/L)'
ATTR_PROCESSTIME = 'Process Time'
ATTR_TEMP = 'Temperature'
ATTR_HUMI = 'Humidity'
ATTR_TODAY_AVG_VALUE = 'Avg. Today'
ATTR_YESTERDAY_AVG_VALUE = 'Avg. Yesterday'
ATTR_DAYS7_AVG_VALUE = 'Avg. 7days'
ATTR_DAYS30_AVG_VALUE = 'Avg. 30days'
ATTR_DAYS90_AVG_VALUE = 'Avg. 90days'

RADONNET_TOKEN_URL='https://radon-net.com/api/auth/signin'
RADONNET_SENSOR_URL = 'https://radon-net.com/api/users/devices?user_id={}'
ARRAFFINITY = 'b6047c7bd277ea708455d8a177742851e53b82ea940a6db8103a0c6e74ef1079'
ARRAFFINITYSAMESITE = 'b6047c7bd277ea708455d8a177742851e53b82ea940a6db8103a0c6e74ef1079'

CONF_USERNAME = 'username'
CONF_PASSWORD = "password"
CONF_NAME = 'name'
CONF_MEASUREMENT = 'measurement'
DEFAULT_NAME = 'Radon Net Sensor'
DEFAULT_MEASUREMENT = 'picocuries'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_MEASUREMENT, default=DEFAULT_MEASUREMENT): vol.In(["picocuries", "bequerels"]),
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    name = config.get(CONF_NAME)
    measurement = config.get(CONF_MEASUREMENT)
    add_entities([RadonNetSensor(username, password, name, measurement)])


class RadonNetSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, username, password, name, measurement):
        """Initialize the sensor."""
        self._state = None
        self._username = username
        self._password = password
        self._name = name
        self._token = None
        self._id = None
#        self._unit_of_measurement = None
        self._measurement = measurement
        self._radon_bq = None
        self._radon_pci = None
        self._sn = None
        self._location = None
        self._dt = None
        self._timezone = None
        self._processtime = None
        self._temp = None
        self._humi = None
        self._today_avg_value = None
        self._yesterday_avg_value = None
        self._days7_avg_value = None
        self._days30_avg_value = None
        self._days90_avg_value = None
        self.update()
    
    def get_session_info(self, session_info):
        header = {
        'X-Requested-With': 'XMLHttpRequest'
        }
        data = {'email': self._username, 'password': self._password}
        try:
            response = requests.post(RADONNET_TOKEN_URL, headers=header, data=data)
            result = response.json()
            _LOGGER.debug('result of get_session_info: %s', result)
            message = result.get('success')
            if message is None:
                return result.get(session_info)
                return None
            elif message == False:
                _LOGGER.debug('Failed to get_session_info: message is False')
                return None
            else:
                _LOGGER.error('Failed to get_session_info: message is NOT None: %s', result)
        except Exception as ex:
            _LOGGER.error('Failed to get_session_info: %s', ex)
            return None
    
    def get_token_id(self):
        if self._id is None:
            self._id = self.get_session_info('ID')
        _LOGGER.debug('ID: %s', self._id)
        if self._token is None:
            self._token = self.get_session_info('Oauth_Token')
        _LOGGER.debug('Token: %s', self._token)

    def conv_str_to_list(strng):
        return json.loads(strng.replace("'", "\""))

    def call_service(self, url):
        cookie = 'user_id=' + str(self._id) + '; user_email=' + self._username +'; token=' + self._token
        header = {
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': cookie
        }
        try:
            response = requests.get(url, headers=header)
            if response.status_code > 400:
                _LOGGER.debug('HTTP status code error: %s', response.status_code)
                if self._id is None:
                    self._id = self.get_session_info('ID')
                _LOGGER.debug('ID: %s', self._id)
                self._token = self.get_session_info('Oauth_Token')
                _LOGGER.debug('Token: %s', self._token)
            #_LOGGER.debug(response)
            result = response.json()
            try:
                message = result.get('success')
            except:
                #_LOGGER.debug('message is null')
                message = None
                _LOGGER.debug('result(1) of call_service: %s', result)
            if message is None:
                return result[0]
            elif message == False:
                _LOGGER.error('call_service error: False result')
                self.get_token_id()
                cookie = 'user_id=' + str(self._id) + '; user_email=' + self._username +'; token=' + self._token
                _LOGGER.debug(cookie)
                header = {
                'X-Requested-With': 'XMLHttpRequest',
                'Cookie': cookie
                }
                response = requests.get(url, headers=header)
                if response.status_code > 400:
                    _LOGGER.debug('HTTP status code error: %s', response.status_code)
                    if self._id is None:
                        self._id = self.get_session_info('ID')
                    _LOGGER.debug('ID: %s', self._id)
                    self._token = self.get_session_info('Oauth_Token')
                    _LOGGER.debug('Token: %s', self._token)
                #_LOGGER.debug(response)
                result = response.json()
                try:
                    message = result.get('success')
                except:
                    #_LOGGER.debug('message is null')
                    message = None
                    _LOGGER.debug('result(2) of call_service: %s', result)
                if message is None:
                    return result[0]
                elif message == False:
                    _LOGGER.debug('call_service error: False result')
                    return None
                else:
                    _LOGGER.debug('result(3) of call_service: %s', result)
                    return result
            else:
                _LOGGER.debug('result(4) of call_service: %s', result)
                return result
        except:
            _LOGGER.debug('call_service error')
            return None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def device_state_attributes(self):
        """Return the optional state attributes."""
        data={}

        data[ATTR_SN] = self._sn
        data[ATTR_LOCATION] = self._location
        data[ATTR_DT] = self._dt
        data[ATTR_TIMEZONE] = self._timezone
        data[ATTR_RADON_BQ] = self._radon_bq
        data[ATTR_RADON_PCI] = self._radon_pci
        data[ATTR_PROCESSTIME] = self._processtime
        data[ATTR_TEMP] = self._temp
        data[ATTR_HUMI] = self._humi
        data[ATTR_TODAY_AVG_VALUE] = self._today_avg_value
        data[ATTR_YESTERDAY_AVG_VALUE] = self._yesterday_avg_value
        data[ATTR_DAYS7_AVG_VALUE] = self._days7_avg_value
        data[ATTR_DAYS30_AVG_VALUE] = self._days30_avg_value
        data[ATTR_DAYS90_AVG_VALUE] = self._days90_avg_value

        return data

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        if self._measurement == 'bequerels':
            return 'Bq/㎥'
        else:
            return 'pCi/L'
    
    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self.get_token_id()
        if self._id is None:
            self.get_token_id()
        elif self._token is None:
            self.get_token_id()
        else:
            url = RADONNET_SENSOR_URL
            url = url.format(self._id)
            result = self.call_service(url)
            if result is None:
                _LOGGER.debug('update -> call_service error')
                return None
            else:
                self._radon_bq = result.get('Radon_Bq')
                self._radon_pci = round(self._radon_bq / 37, 2)
                self._sn = result.get('SN')
                self._location = result.get('Location')
                self._dt = result.get('DT')
                self._timezone = result.get('TimeZone')
                self._processtime = result.get('ProcessTime')
                self._temp = result.get('Temp')
                self._humi = result.get('Humi')
                if self._measurement == 'bequerels':
                    self._state = self._radon_bq
                    self._today_avg_value = result.get('Today_Avg_Value')
                    self._yesterday_avg_value = result.get('Yesterday_Avg_Value')
                    self._days7_avg_value = result.get('Days7_Avg_Value')
                    self._days30_avg_value = result.get('Days30_Avg_Value')
                    self._days90_avg_value = result.get('Days90_Avg_Value')
                else:
                    self._state = self._radon_pci
                    self._today_avg_value = round(result.get('Today_Avg_Value') / 37, 2)
                    self._yesterday_avg_value = round(result.get('Yesterday_Avg_Value') / 37, 2)
                    self._days7_avg_value = round(result.get('Days7_Avg_Value') / 37, 2)
                    self._days30_avg_value = round(result.get('Days30_Avg_Value') / 37, 2)
                    self._days90_avg_value = round(result.get('Days90_Avg_Value') / 37, 2)
