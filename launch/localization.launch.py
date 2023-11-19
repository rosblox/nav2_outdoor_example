#/bin/python3

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    pkg_share = get_package_share_directory('nav2_outdoor_example')

  
    map_transform_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_transform',
        output='screen',
        arguments = "--x -1 --y 0 --z 0 --roll 0 --pitch 0 --yaw 0 --frame-id map --child-frame-id odom".split(' '),
        )
    
    navsat_transform_node = Node(
        package='robot_localization',
        executable='navsat_transform_node',
        name='navsat_transform_node',
        output='screen',
        parameters=[{
            "magnetic_declination_radians": 0.05,
            "yaw_offset": 0.0,
            "zero_altitude": False,
            "use_odometry_yaw": False,
            "wait_for_datum": False,
            "publish_filtered_gps": False,
            "broadcast_utm_transform": False,
            "use_simtime": True,
            "delay": 3.0,
        }],
        remappings=[
            ('/odometry/filtered', '/odom'),
            ('/imu','/imu/data'),
        ]
        )

    ukf_localization_node = Node(
        package='robot_localization',
        executable='ukf_node',
        name='ukf_node',
        output='screen',
        respawn=True,
        parameters=[os.path.join(pkg_share, 'config/ukf.yaml')],
        remappings=[
            ('/odometry/filtered', '/odom'),
        ]
        )


    complementary_filter_node = Node(
                package='imu_complementary_filter',
                executable='complementary_filter_node',
                name='complementary_filter_gain_node',
                output='screen',
                parameters=[
                    {'do_bias_estimation': True},
                    {'do_adaptive_gain': True},
                    {'use_mag': True},
                    {'gain_acc': 0.1},
                    {'gain_mag': 0.1},
                ],
            )


    return LaunchDescription(
        [
            complementary_filter_node,
            ukf_localization_node,
            navsat_transform_node,
            map_transform_node,
        ]
    )


