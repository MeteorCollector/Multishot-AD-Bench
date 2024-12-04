#!/usr/bin/env python

# Copyright (c) 2019 Intel Corporation
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""
Wrapper for autonomous agents required for tracking and checking of used sensors
"""

from __future__ import print_function
import math
import os

import carla
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider

from leaderboard.autoagents.autonomous_agent import Track

from leaderboard.envs.sensor_interface import CallBack, OpenDriveMapReader, SpeedometerReader, SensorConfigurationInvalid
# Use this line instead to run WOR
#from leaderboard1.leaderboard.envs.sensor_interface import (CallBack, StitchCameraReader, OpenDriveMapReader, SpeedometerReader, SensorConfigurationInvalid)

DATAGEN = int(os.environ.get('DATAGEN'))
MAX_ALLOWED_RADIUS_SENSOR = 10.0

SENSORS_LIMITS = {
    'sensor.camera.rgb': 6,
    'sensor.lidar.ray_cast': 1,
    'sensor.other.radar': 5,
    'sensor.other.gnss': 1,
    'sensor.other.imu': 1,
    'sensor.opendrive_map': 1,
    'sensor.speedometer': 1,
    'sensor.stitch_camera.rgb': 1,
    'sensor.camera.depth': 4, # for data generation
    'sensor.camera.semantic_segmentation': 4 # for data generation
}


class AgentError(Exception):
    """
    Exceptions thrown when the agent returns an error during the simulation
    """

    def __init__(self, message):
        super(AgentError, self).__init__(message)


class AgentWrapper(object):

    """
    Wrapper for autonomous agents required for tracking and checking of used sensors
    """

    allowed_sensors = [
        'sensor.opendrive_map',
        'sensor.speedometer',
        'sensor.camera.rgb',
        'sensor.camera',
        'sensor.lidar.ray_cast',
        'sensor.other.radar',
        'sensor.other.gnss',
        'sensor.other.imu',
        'sensor.stitch_camera.rgb', # for World on Rails eval
        'sensor.camera.depth', # for data generation
        'sensor.camera.semantic_segmentation', # for data generation
    ]

    _agent = None
    _sensors_list = []

    def __init__(self, agent):
        """
        Set the autonomous agent
        """
        self._agent = agent

    def __call__(self):
        """
        Pass the call directly to the agent
        """
        return self._agent()

    def setup_sensors(self, vehicle, debug_mode=False):
        """
        Create the sensors defined by the user and attach them to the ego-vehicle
        :param vehicle: ego vehicle
        :return:
        """
        bp_library = CarlaDataProvider.get_world().get_blueprint_library()
        for sensor_spec in self._agent.sensors():
            # These are the pseudosensors (not spawned)
            if sensor_spec['type'].startswith('sensor.opendrive_map'):
                # The HDMap pseudo sensor is created directly here
                sensor = OpenDriveMapReader(vehicle, sensor_spec['reading_frequency'])
            elif sensor_spec['type'].startswith('sensor.speedometer'):
                delta_time = CarlaDataProvider.get_world().get_settings().fixed_delta_seconds
                frame_rate = 1 / delta_time
                sensor = SpeedometerReader(vehicle, frame_rate)
            elif sensor_spec['type'].startswith('sensor.stitch_camera'):
                delta_time = CarlaDataProvider.get_world().get_settings().fixed_delta_seconds
                frame_rate = 1 / delta_time
                sensor = StitchCameraReader(bp_library, vehicle, sensor_spec, frame_rate)
            # These are the sensors spawned on the carla world
            else:
                bp = bp_library.find(str(sensor_spec['type']))
                if sensor_spec['type'].startswith('sensor.camera'):
                    bp.set_attribute('image_size_x', str(sensor_spec['width']))
                    bp.set_attribute('image_size_y', str(sensor_spec['height']))

                    # added attrubute to adapt to nuScene.
                    bp.set_attribute('sensor_tick', str(sensor_spec['sensor_tick']))
                    bp.set_attribute('fstop', str(sensor_spec['fstop']))
                    bp.set_attribute('shutter_speed', str(sensor_spec['shutter_speed']))
                    # end of augmentation

                    bp.set_attribute('fov', str(sensor_spec['fov']))
                    if DATAGEN==0:
                        bp.set_attribute('lens_circle_multiplier', str(3.0))
                        bp.set_attribute('lens_circle_falloff', str(3.0))
                    if sensor_spec['type'].startswith('sensor.camera.rgb'):
                        bp.set_attribute('chromatic_aberration_intensity', str(0.5))
                        bp.set_attribute('chromatic_aberration_offset', str(0))

                    sensor_location = carla.Location(x=sensor_spec['x'], y=sensor_spec['y'],
                                                     z=sensor_spec['z'])
                    sensor_rotation = carla.Rotation(pitch=sensor_spec['pitch'],
                                                     roll=sensor_spec['roll'],
                                                     yaw=sensor_spec['yaw'])
                elif sensor_spec['type'].startswith('sensor.lidar'):
                    bp.set_attribute('range', str(sensor_spec['range']))
                    if DATAGEN==1:
                        bp.set_attribute('rotation_frequency', str(sensor_spec['rotation_frequency']))
                        bp.set_attribute('points_per_second', str(sensor_spec['points_per_second']))
                    else:
                        bp.set_attribute('rotation_frequency', str(100))
                        bp.set_attribute('points_per_second', str(1400000))
                    bp.set_attribute('channels', str(sensor_spec['channels']))
                    bp.set_attribute('upper_fov', str(sensor_spec['upper_fov']))
                    bp.set_attribute('lower_fov', str(sensor_spec['lower_fov']))
                    # bp.set_attribute('horizontal_fov', str(sensor_spec['horizontal_fov']))
                    # in older versions of Carla, horizontal_fov is set to 360.
                    bp.set_attribute('sensor_tick', str(sensor_spec['sensor_tick']))
                    bp.set_attribute('atmosphere_attenuation_rate', str(0.004))
                    bp.set_attribute('dropoff_general_rate', str(0.45))
                    bp.set_attribute('dropoff_intensity_limit', str(0.8))
                    bp.set_attribute('dropoff_zero_intensity', str(0.4))
                    sensor_location = carla.Location(x=sensor_spec['x'], y=sensor_spec['y'],
                                                     z=sensor_spec['z'])
                    sensor_rotation = carla.Rotation(pitch=sensor_spec['pitch'],
                                                     roll=sensor_spec['roll'],
                                                     yaw=sensor_spec['yaw'])
                elif sensor_spec['type'].startswith('sensor.other.radar'):
                    bp.set_attribute('horizontal_fov', str(sensor_spec['horizontal_fov']))  # degrees
                    bp.set_attribute('vertical_fov', str(sensor_spec['vertical_fov']))  # degrees
                    bp.set_attribute('points_per_second', '1500')
                    bp.set_attribute('range', '250')  # meters

                    # added attrubute to adapt to nuScene.
                    bp.set_attribute('sensor_tick', '0.076923')
                    # end of augmentation

                    sensor_location = carla.Location(x=sensor_spec['x'],
                                                     y=sensor_spec['y'],
                                                     z=sensor_spec['z'])
                    sensor_rotation = carla.Rotation(pitch=sensor_spec['pitch'],
                                                     roll=sensor_spec['roll'],
                                                     yaw=sensor_spec['yaw'])

                elif sensor_spec['type'].startswith('sensor.other.gnss'):
                    if DATAGEN==0:
                        bp.set_attribute('noise_alt_stddev', str(0.000005))
                        bp.set_attribute('noise_lat_stddev', str(0.000005))
                        bp.set_attribute('noise_lon_stddev', str(0.000005))
                    bp.set_attribute('noise_alt_bias', str(0.0))
                    bp.set_attribute('noise_lat_bias', str(0.0))
                    bp.set_attribute('noise_lon_bias', str(0.0))

                    sensor_location = carla.Location(x=sensor_spec['x'],
                                                     y=sensor_spec['y'],
                                                     z=sensor_spec['z'])
                    sensor_rotation = carla.Rotation()

                elif sensor_spec['type'].startswith('sensor.other.imu'):
                    bp.set_attribute('noise_accel_stddev_x', str(0.001))
                    bp.set_attribute('noise_accel_stddev_y', str(0.001))
                    bp.set_attribute('noise_accel_stddev_z', str(0.015))
                    bp.set_attribute('noise_gyro_stddev_x', str(0.001))
                    bp.set_attribute('noise_gyro_stddev_y', str(0.001))
                    bp.set_attribute('noise_gyro_stddev_z', str(0.001))

                    sensor_location = carla.Location(x=sensor_spec['x'],
                                                     y=sensor_spec['y'],
                                                     z=sensor_spec['z'])
                    sensor_rotation = carla.Rotation(pitch=sensor_spec['pitch'],
                                                     roll=sensor_spec['roll'],
                                                     yaw=sensor_spec['yaw'])
                # create sensor
                sensor_transform = carla.Transform(sensor_location, sensor_rotation)
                sensor = CarlaDataProvider.get_world().spawn_actor(bp, sensor_transform, vehicle)
            # setup callback
            sensor.listen(CallBack(sensor_spec['id'], sensor_spec['type'], sensor, self._agent.sensor_interface))
            self._sensors_list.append(sensor)

        # Tick once to spawn the sensors
        CarlaDataProvider.get_world().tick()


    @staticmethod
    def validate_sensor_configuration(sensors, agent_track, selected_track):
        """
        Ensure that the sensor configuration is valid, in case the challenge mode is used
        Returns true on valid configuration, false otherwise
        """
        if Track(selected_track) != agent_track:
            raise SensorConfigurationInvalid("You are submitting to the wrong track [{}]!".format(Track(selected_track)))

        sensor_count = {}
        sensor_ids = []

        for sensor in sensors:

            # Check if the is has been already used
            sensor_id = sensor['id']
            if sensor_id in sensor_ids:
                raise SensorConfigurationInvalid("Duplicated sensor tag [{}]".format(sensor_id))
            else:
                sensor_ids.append(sensor_id)

            # Check if the sensor is valid
            if agent_track == Track.SENSORS:
                if sensor['type'].startswith('sensor.opendrive_map'):
                    raise SensorConfigurationInvalid("Illegal sensor used for Track [{}]!".format(agent_track))

            # Check the sensors validity
            if sensor['type'] not in AgentWrapper.allowed_sensors:
                raise SensorConfigurationInvalid("Illegal sensor used. {} are not allowed!".format(sensor['type']))

            # Check the extrinsics of the sensor
            if 'x' in sensor and 'y' in sensor and 'z' in sensor:
                if math.sqrt(sensor['x']**2 + sensor['y']**2 + sensor['z']**2) > MAX_ALLOWED_RADIUS_SENSOR:
                    raise SensorConfigurationInvalid(
                        "Illegal sensor extrinsics used for Track [{}]!".format(agent_track))

            # Check the amount of sensors
            if sensor['type'] in sensor_count:
                sensor_count[sensor['type']] += 1
            else:
                sensor_count[sensor['type']] = 1


        for sensor_type, max_instances_allowed in SENSORS_LIMITS.items():
            if sensor_type in sensor_count and sensor_count[sensor_type] > max_instances_allowed:
                raise SensorConfigurationInvalid(
                    "Too many {} used! "
                    "Maximum number allowed is {}, but {} were requested.".format(sensor_type,
                                                                                  max_instances_allowed,
                                                                                  sensor_count[sensor_type]))

    def cleanup(self):
        """
        Remove and destroy all sensors
        """
        for i, _ in enumerate(self._sensors_list):
            if self._sensors_list[i] is not None:
                self._sensors_list[i].stop()
                self._sensors_list[i].destroy()
                self._sensors_list[i] = None
        self._sensors_list = []
