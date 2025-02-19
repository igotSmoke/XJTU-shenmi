void Scene::simulation_update()
{
   
    // 这次模拟的总时长不是上一帧的时长，而是上一帧时长与之前帧剩余时长的总和，
    // 即上次调用 simulation_update 到现在过了多久。
    // 以固定的时间步长 (time_step) 循环模拟物体运动，每模拟一步，模拟总时长就减去一个
    // time_step ，当总时长不够一个 time_step 时停止模拟。
    // 根据刚才模拟时间步的数量，更新最后一次调用 simulation_update 的时间 (last_update)。
    
    //每一帧的渲染过程可以概括为更新数据（几何、运动等等）和渲染图像两步。 
    // 约定当前屏幕上显示的是上一帧的图像，正在计算的是当前帧的数据。 
    // 更新运动状态时首先用当前时间减去 last_update 得到上一帧和之前帧剩余时长之和； 
    // 再循环模拟物体运动。每循环一次走过一个长度为 time_step 的时间步、 剩余时长减去 time_step ；
    // 当剩余时长不足一个 time_step 时停止模拟， 并将这一帧模拟走过的总时长累加到 last_update 上。

     time_point now_time = steady_clock::now();
     duration now_to_last = now_time - last_update;
     float nowtolast_length = now_to_last.count();
     while (nowtolast_length >= time_step)
     {
         for (auto& group : groups) 
         {
             for (auto& object : group->objects) 
             {
                 object->update(all_objects);
             }
         }
         nowtolast_length -= time_step;
     }
     duration frame_length = duration(now_to_last.count() - nowtolast_length);
     last_update += duration_cast<time_point::duration>(frame_length);

 




}
void Object::update(vector<Object*>& all_objects)
{
    // 首先调用 step 函数计下一步该物体的运动学状态。
    KineticState current_state{center, velocity, force / mass};
    KineticState next_state = step(prev_state, current_state);
    center                  = next_state.position;
    //velocity                = next_state.velocity;
    
    // 将物体的位置移动到下一步状态处，但暂时不要修改物体的速度。
    // 遍历 all_objects，检查该物体在下一步状态的位置处是否会与其他物体发生碰撞。
    bool if_coop = false;
    for (auto object : all_objects) 
    {
        if (id == object->id && name == object->name)
            continue;
        
        Intersection coop_result;
        for (size_t i = 0; i < mesh.edges.count(); ++i) 
        {
            array<size_t, 2> v_indices = mesh.edge(i);
            Vector3f point_1           = mesh.vertex(v_indices[0]);
            Vector3f point_2           = mesh.vertex(v_indices[1]);
            Eigen::Vector4f point_14   = {point_1[0], point_1[1], point_1[2], 1.0f};
            Eigen::Vector4f point_24   = {point_2[0], point_2[1], point_2[2], 1.0f};
            point_14                   =  model()* point_14;
            point_24                   =  model() * point_24;
            point_1[0] = point_14[0];
            point_1[1] = point_14[1];
            point_1[2] = point_14[2];
            point_2[0] = point_24[0];
            point_2[1] = point_24[1];
            point_2[2] = point_24[2];

            Ray ray1to2;
            ray1to2.origin    = point_1;
            ray1to2.direction = point_2 - point_1;
            optional<Intersection> result1to2 =
                naive_intersect(ray1to2, object->mesh, object->model());

            Ray ray2to1;
            ray2to1.origin    = point_2;
            ray2to1.direction = point_1 - point_2;
            optional<Intersection> result2to1 =
                naive_intersect(ray2to1, object->mesh, object->model());

            Intersection result21;
            Intersection result12;
            
            if (result2to1.has_value())
            {
                result21 = result2to1.value();
                if (result21.t <= 1 && result21.t > 0 )
                {
                    coop_result = result21;
                    if_coop     = true;
                    break;
                }         
            }
            if (result1to2.has_value()) 
            {
                result12 = result1to2.value();
                if (result12.t <= 1 && result12.t > 0 )
                {
                    coop_result = result12;
                    if_coop     = true;
                    break;
                }       
            }    
        }

        if (if_coop)
        {
            //logger->info("bei zhuang de ID: {}", object->id); 
            //logger->info("beizhuang mian ID: {}", coop_result.face_index); 
            Vector3f point_A = object->mesh.vertex(object->mesh.face(coop_result.face_index)[0]);
            Vector3f point_B = object->mesh.vertex(object->mesh.face(coop_result.face_index)[1]);
            Vector3f point_C = object->mesh.vertex(object->mesh.face(coop_result.face_index)[2]);
            

            //logger->info("Vector3f: (x: {}, y: {}, z: {})", point_A[0], point_A[1], point_A[2]);
           // logger->info("Vector3f: (x: {}, y: {}, z: {})", point_B[0], point_B[1], point_B[2]);
           // logger->info("Vector3f: (x: {}, y: {}, z: {})", point_C[0], point_C[1], point_C[2]);

            Eigen::Vector4f point_A4 = {point_A[0], point_A[1], point_A[2], 1.0f};
            Eigen::Vector4f point_B4 = {point_B[0], point_B[1], point_B[2], 1.0f};
            Eigen::Vector4f point_C4 = {point_C[0], point_C[1], point_C[2], 1.0f};

            point_A4 = object->model() * point_A4;
            point_B4 = object->model() * point_B4;
            point_C4 = object->model() * point_C4;

            point_A[0] = point_A4[0];
            point_A[1] = point_A4[1];
            point_A[2] = point_A4[2];
            point_B[0] = point_B4[0];
            point_B[1] = point_B4[1];
            point_B[2] = point_B4[2];
            point_C[0] = point_C4[0];
            point_C[1] = point_C4[1];
            point_C[2] = point_C4[2];

            Vector3f A_sub_B = point_A - point_B;
            Vector3f A_sub_C = point_A - point_C;
            Vector3f n       = A_sub_B.cross(A_sub_C);
            n                = n.normalized();

            
            
            Vector3f v1_sub_v2 = object->velocity - velocity;
            float Jr           = 2 * v1_sub_v2.dot(n) * (mass * object->mass )/( mass + object->mass);
            velocity = velocity + (Jr / mass) * n;
            object->velocity   = object->velocity - (Jr / object->mass) * n;
            object->center     = object->prev_state.position;
            
            
            //logger->info("faxiangliang: (x: {}, y: {}, z: {})", n[0], n[1], n[2]);
           // logger->info("Vector3f: (x: {}, y: {}, z: {})", point_A[0], point_A[1], point_A[2]);
            //logger->info("Vector3f: (x: {}, y: {}, z: {})", point_B[0], point_B[1], point_B[2]);
            //logger->info("Vector3f: (x: {}, y: {}, z: {})", point_C[0], point_C[1], point_C[2]);

            center = current_state.position;
           
            break;
        }
    }
    prev_state = current_state;
    if (!if_coop)
        velocity   = next_state.velocity;
}
KineticState forward_euler_step([[maybe_unused]] const KineticState& previous,
                                const KineticState& current)
{
    KineticState new_state;
    new_state.acceleration = current.acceleration;
    new_state.velocity     = current.velocity + current.acceleration * time_step;
    new_state.position     = current.position + current.velocity * time_step;

    return new_state;
}