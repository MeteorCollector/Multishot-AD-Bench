import carla

# 设置相机传感器并附加到车辆上
def attach_camera_to_vehicle(world, vehicle):
    blueprint_library = world.get_blueprint_library()
    
    # 获取RGB相机蓝图
    camera_bp = blueprint_library.find('sensor.camera.rgb')
    
    # 设置相机分辨率和其他参数
    camera_bp.set_attribute('image_size_x', '800')
    camera_bp.set_attribute('image_size_y', '600')
    camera_bp.set_attribute('fov', '90')

    # 将相机附加到车辆上，设置它的位置
    spawn_point = carla.Transform(carla.Location(x=1.5, z=2.4))  # 调整相机位置
    camera = world.spawn_actor(camera_bp, spawn_point, attach_to=vehicle)
    
    return camera

# 图像保存的回调函数
def save_image(image, save_path, frame_id):
    image.convert(carla.ColorConverter.Raw)
    filename = f"{save_path}/{frame_id:05d}.png"  # 按编号存储，五位递增
    image.save_to_disk(filename)