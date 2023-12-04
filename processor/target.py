#!/usr/bin/python3
import os, sys, time, json, traceback, 
from datetime import datetime, timedelta, timezone


## This is the definition for a tiny lambda function
## Which is run in response to messages processed in Doover's 'Channels' system

## In the doover_config.json file we have defined some of these subscriptions
## These are under 'processor_deployments' > 'tasks'


## You can import the pydoover module to interact with Doover based on decisions made in this function
## Just add the current directory to the path first

## attempt to delete any loaded pydoover modules that persist across lambdas


if 'pydoover' in sys.modules:
    del sys.modules['pydoover']
try: del pydoover
except: pass
try: del pd
except: pass

# sys.path.append(os.path.dirname(__file__))
import pydoover as pd


class target:

    def __init__(self, *args, **kwargs):

        self.kwargs = kwargs
        ### kwarg
        #     'agent_id' : The Doover agent id invoking the task e.g. '9843b273-6580-4520-bdb0-0afb7bfec049'
        #     'access_token' : A temporary token that can be used to interact with the Doover API .e.g 'ABCDEFGHJKLMNOPQRSTUVWXYZ123456890',
        #     'api_endpoint' : The API endpoint to interact with e.g. "https://my.doover.com",
        #     'package_config' : A dictionary object with configuration for the task - as stored in the task channel in Doover,
        #     'msg_obj' : A dictionary object of the msg that has invoked this task,
        #     'task_id' : The identifier string of the task channel used to run this processor,
        #     'log_channel' : The identifier string of the channel to publish any logs to
        #     'agent_settings' : {
        #       'deployment_config' : {} # a dictionary of the deployment config for this agent
        #     }


    ## This function is invoked after the singleton instance is created
    def execute(self):

        start_time = time.time()

        self.create_doover_client()

        self.add_to_log( "kwargs = " + str(self.kwargs) )
        self.add_to_log( str( start_time ) )

        try:

            ## Get the oem_uplink channel
            oem_uplink_channel = self.cli.get_channel(
                channel_name= "rypar_oem_uplink_recv",
                agent_id=self.kwargs['agent_id']
            )

            ## Get the state channel
            ui_state_channel = self.cli.get_channel(
                channel_name="ui_state",
                agent_id=self.kwargs['agent_id']
            )

            ## Get the cmds channel
            ui_cmds_channel = self.cli.get_channel(
                channel_name="ui_cmds",
                agent_id=self.kwargs['agent_id']
            )

            ## Get the location channel
            location_channel = self.cli.get_channel(
                channel_name="location",
                agent_id=self.kwargs['agent_id']
            )
            
            ## Do any processing you would like to do here
            message_type = None
            if 'message_type' in self.kwargs['package_config'] and 'message_type' is not None:
                message_type = self.kwargs['package_config']['message_type']

            if message_type == "DEPLOY":
                self.deploy(oem_uplink_channel, ui_state_channel, ui_cmds_channel, location_channel)

            if message_type == "DOWNLINK":
                self.downlink(oem_uplink_channel, ui_state_channel, ui_cmds_channel, location_channel)

            if message_type == "UPLINK":
                self.uplink(oem_uplink_channel, ui_state_channel, ui_cmds_channel, location_channel)

        except Exception as e:
            self.add_to_log("ERROR attempting to process message - " + str(e))
            self.add_to_log(traceback.format_exc())

        self.complete_log()



    def deploy(self, oem_uplink_channel, ui_state_channel, ui_cmds_channel, location_channel):
        ## Run any deployment code here

        ui_obj = {
            "state" : {
                "type" : "uiContainer",
                "displayString" : "",
                "children" : {
                    "location" : {
                        "type" : "uiVariable",
                        "varType" : "location",
                        "hide" : True,
                        "name" : "location",
                        "displayString" : "Location",
                    },
                    "sensorReading" : {
                        "type" : "uiVariable",
                        "varType" : "float",
                        "name" : "sensorReading",
                        "displayString" : "Sensor Reading",
                        "decPrecision": 1,
                        "form": "radialGauge",
                        "ranges": [
                            {
                                "label" : "Low",
                                "min" : 0,
                                "max" : 20,
                                "colour" : "blue",
                                "showOnGraph" : True
                            },
                            {
                                # "label" : "Ok",
                                "min" : 20,
                                "max" : 80,
                                "colour" : "green",
                                "showOnGraph" : True
                            },
                            {
                                "label" : "Fast",
                                "min" : 80,
                                "max" : 120,
                                "colour" : "yellow",
                                "showOnGraph" : True
                            }
                        ]
                    },
                    "sensorLastRead": {
                        "type" : "uiVariable",
                        "varType" : "text",
                        "name" : "sensorLastRead",
                        "displayString" : "Last Reading",
                    },
                    "battVoltage" : {
                        "type" : "uiVariable",
                        "varType" : "float",
                        "name" : "battVoltage",
                        "displayString" : "Battery (V)",
                        "decPrecision": 1,
                        "ranges": [
                            {
                                "label" : "Low",
                                "min" : 3.0,
                                "max" : 3.5,
                                "colour" : "yellow",
                                "showOnGraph" : True
                            },
                            {
                                # "label" : "Ok",
                                "min" : 3.5,
                                "max" : 3.8,
                                "colour" : "blue",
                                "showOnGraph" : True
                            },
                            {
                                "label" : "Good",
                                "min" : 3.8,
                                "max" : 4.2,
                                "colour" : "green",
                                "showOnGraph" : True
                            },
                            {
                                "label" : "Over Voltage",
                                "min" : 4.2,
                                "max" : 4.5,
                                "colour" : "yellow",
                                "showOnGraph" : True
                            }
                        ]
                    },
                    "settings_submodule": {
                        "type": "uiSubmodule",
                        "name": "settings_submodule",
                        "displayString": "Settings",
                        "children": {
                            "gpsAccuracy" : {
                                "type" : "uiVariable",
                                "varType" : "float",
                                "name" : "gpsAccuracy",
                                "displayString" : "GPS accuracy (m)",
                                "decPrecision": 0,
                                "ranges": [
                                    {
                                        "label" : "Good",
                                        "min" : 0,
                                        "max" : 15,
                                        "colour" : "green",
                                        "showOnGraph" : True
                                    },
                                    {
                                        "label" : "Ok",
                                        "min" : 15,
                                        "max" : 30,
                                        "colour" : "blue",
                                        "showOnGraph" : True
                                    },
                                    {
                                        "label" : "Bad",
                                        "min" : 30,
                                        "max" : 80,
                                        "colour" : "yellow",
                                        "showOnGraph" : True
                                    },
                                    {
                                        "label" : "Lost",
                                        "min" : 80,
                                        "max" : 100,
                                        "colour" : "red",
                                        "showOnGraph" : True
                                    }
                                ]
                            },
                            "debug_submodule": {
                                "type": "uiSubmodule",
                                "name": "debug_submodule",
                                "displayString": "Debug",
                                "children": {
                                    "deviceImei" : {
                                        "type" : "uiVariable",
                                        "varType" : "text",
                                        "name" : "deviceImei",
                                        "displayString" : "Device IMEI",
                                    },
                                    "sensorName" : {
                                        "type" : "uiVariable",
                                        "varType" : "text",
                                        "name" : "sensorName",
                                        "displayString" : "Sensor Name",
                                    },
                                    "sensorUnits" : {
                                        "type" : "uiVariable",
                                        "varType" : "text",
                                        "name" : "sensorUnits",
                                        "displayString" : "Sensor Units",
                                    },
                                    "systemFreeHeap" : {
                                        "type" : "uiVariable",
                                        "varType" : "float",
                                        "name" : "systemFreeHeap",
                                        "displayString" : "System Free Heap (bytes)",
                                        "decPrecision": 2,
                                    },
                                    "systemThrottled" : {
                                        "type" : "uiVariable",
                                        "varType" : "bool",
                                        "name" : "systemThrottled",
                                        "displayString" : "System Throttled",
                                    },
                                    "sdCardSize": {
                                        "type" : "uiVariable",
                                        "varType" : "float",
                                        "name" : "sdCardSize",
                                        "displayString" : "SD Card Size (GB)",
                                    },
                                    "sdUtilization": {
                                        "type" : "uiVariable",
                                        "varType" : "float",
                                        "name" : "sdUtilization",
                                        "displayString" : "SD Card Utilization (%)",
                                    },
                                    "gpsFixTime" : {
                                        "type" : "uiVariable",
                                        "varType" : "float",
                                        "name" : "gpsFixTime",
                                        "displayString" : "GPS Fix Time (sec)",
                                        "decPrecision": 1,
                                    },
                                    "systemResetUuid" : {
                                        "type" : "uiVariable",
                                        "varType" : "text",
                                        "name" : "systemResetUuid",
                                        "displayString" : "System Reset UUID",
                                    },
                                    "dataSignalStrength" : {
                                        "type" : "uiVariable",
                                        "varType" : "float",
                                        "name" : "dataSignalStrength",
                                        "displayString" : "Cellular Signal (dbm)",
                                        "decPrecision": 0,
                                    },
                                    "deviceTemp" : {
                                        "type" : "uiVariable",
                                        "varType" : "float",
                                        "name" : "deviceTemp",
                                        "displayString" : "Device Temperature (C)",
                                        "decPrecision": 0,
                                        "ranges": [
                                            {
                                                "label" : "Low",
                                                "min" : 0,
                                                "max" : 20,
                                                "colour" : "blue",
                                                "showOnGraph" : True
                                            },
                                            {
                                                # "label" : "Ok",
                                                "min" : 20,
                                                "max" : 35,
                                                "colour" : "green",
                                                "showOnGraph" : True
                                            },
                                            {
                                                "label" : "Warm",
                                                "min" : 35,
                                                "max" : 50,
                                                "colour" : "yellow",
                                                "showOnGraph" : True
                                            }
                                        ]
                                    },
                                    # "lastUplinkReason" : {
                                    #     "type" : "uiVariable",
                                    #     "varType" : "text",
                                    #     "name" : "lastUplinkReason",
                                    #     "displayString" : "Reason for uplink",
                                    # },
                                    # "deviceTimeUtc" : {
                                    #     "type" : "uiVariable",
                                    #     "varType" : "datetime",
                                    #     "name" : "deviceTimeUtc",
                                    #     "displayString" : "Device Time (UTC)",
                                    # },
                                    # "node_connection_info": {
                                    #     "type": "uiConnectionInfo",
                                    #     "name": "node_connection_info",
                                    #     "connectionType": "periodic",
                                    #     # "connectionPeriod": 1800,
                                    #     # "nextConnection": 1800
                                    #     "connectionPeriod": 600,
                                    #     "nextConnection": 600,
                                    # }
                                }
                            }
                        }
                    }
                }
            }
        }

        ui_state_channel.publish(
            msg_str=json.dumps(ui_obj)
        )

        ## Publish a dummy message to oem_uplink to trigger a new process of data
        oem_uplink_channel.publish(
            msg_str=json.dumps({}),
            save_log=False,
            log_aggregate=False
        )


    def downlink(self, oem_uplink_channel, ui_state_channel, ui_cmds_channel, location_channel):
        ## Run any downlink processing code here
        pass


    def uplink(self, oem_uplink_channel, ui_state_channel, ui_cmds_channel, location_channel):
        ## Run any uplink processing code here

        if 'msg_obj' in self.kwargs and self.kwargs['msg_obj'] is not None:
            msg_id = self.kwargs['msg_obj']['message']
            channel_id = self.kwargs['msg_obj']['channel']
            payload = self.kwargs['msg_obj']['payload']

        if not msg_id:
            self.add_to_log( "No trigger message passed - skipping processing" )
            return
        
        device_id = payload['s']
        reading = payload['s1Value']
        sensor_name = payload['s1Sensor']
        reading_units = payload['s1Units']
        last_reading = payload['unix_s']

        utc_datetime = datetime.utcfromtimestamp(last_reading).replace(tzinfo=timezone.utc)
        aest_offset = timedelta(hours=10)
        # Convert UTC datetime to AEST datetime
        aest_datetime = utc_datetime.astimezone(timezone(aest_offset))
        # Format the AEST datetime as a string
        aest_string = aest_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')

        device_lat = payload['la']
        device_long = payload['lo']

        signal_strength = payload['rsrp']
        battery_voltage = payload['bv']
        device_temp = payload['bt']
        gps_acc = payload['ac']
        gps_fix_time = payload['ti']
        sd_size = payload['ss']
        sd_util = payload['sf']
        throttle = payload['th']
        free_heap = payload['sh']
        reset_uuid = payload['sr']


        position = {
            'lat': device_lat,
            'long': device_long,
        }

        # position = {
        #     'lat': f['Lat'],
        #     'long': f['Long'],
        #     'alt': f['Alt'],
        # }

        self.add_to_log( "Received uplink message - " + str(msg_id) )

        

        if not bool(payload):
            self.add_to_log( "No payload in message - skipping processing" )
            return

        ui_state_channel.publish(
            msg_str=json.dumps({
                "state" : {
                    # "displayString" : display_string,
                    # "statusIcon" : status_icon,
                    "children" : {
                        "location" : {
                            "currentValue" : position,
                        },
                        "sensorReading" : {
                            "displayString" : f"{sensor_name} ({reading_units})",
                            "currentValue" : reading,
                        },
                        "sensorLastRead": {
                            "currentValue" : aest_string,
                        },
                        "battVoltage": {
                            "currentValue" : battery_voltage,
                        },
                        "settings_submodule": {
                            "children": {
                                "gpsAccuracy" : {
                                    "currentValue" : gps_acc,
                                },
                                "debug_submodule" : {
                                    "children":{
                                        "deviceImei" : {
                                            "currentValue" : device_id,
                                        },
                                        "sensorName" : {
                                            "currentValue" : sensor_name,
                                        },
                                        "sensorUnits" : {
                                            "currentValue" : reading_units,
                                        },
                                        "systemFreeHeap" : {
                                            "currentValue" : free_heap,
                                        },
                                        "systemThrottled" : {
                                            "currentValue" : throttle,
                                        },
                                        "sdCardSize" : {
                                            "currentValue" : sd_size,
                                        },
                                        "sdUtilization" : {
                                            "currentValue" : sd_util,
                                        },
                                        "gpsFixTime" : {
                                            "currentValue" : gps_fix_time,
                                        },
                                        "systemResetUuid" : {
                                            "currentValue" : reset_uuid,
                                        },
                                        "dataSignalStrength" : {
                                            "currentValue" : signal_strength,
                                        },
                                        "deviceTemp" : {
                                            "currentValue" : device_temp,
                                        },
                                    }
                                }
                            }
                        }
                    }
                }
            }),
            save_log=True
        )

    def create_doover_client(self):
        self.cli = pd.doover_iface(
            agent_id=self.kwargs['agent_id'],
            access_token=self.kwargs['access_token'],
            endpoint=self.kwargs['api_endpoint'],
        )

    def add_to_log(self, msg):
        if not hasattr(self, '_log'):
            self._log = ""
        self._log = self._log + str(msg) + "\n"

    def complete_log(self):
        if hasattr(self, '_log') and self._log is not None:
            log_channel = self.cli.get_channel( channel_id=self.kwargs['log_channel'] )
            log_channel.publish(
                msg_str=self._log
            )
