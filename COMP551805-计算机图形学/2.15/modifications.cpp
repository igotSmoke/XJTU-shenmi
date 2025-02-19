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
optional<Intersection> naive_intersect(const Ray& ray, const GL::Mesh& mesh, const Matrix4f model)
{
    Intersection result;


    for (size_t i = 0; i < mesh.faces.count(); ++i) 
    {
        Vector3f point_A          = mesh.vertex(mesh.face(i)[0]);
        Vector3f point_B          = mesh.vertex(mesh.face(i)[1]);
        Vector3f point_C          = mesh.vertex(mesh.face(i)[2]);

        Vector4f point_A4         = {point_A[0], point_A[1], point_A[2], 1.0f};
        Vector4f point_B4         = {point_B[0], point_B[1], point_B[2], 1.0f};
        Vector4f point_C4         = {point_C[0], point_C[1], point_C[2], 1.0f};

        point_A4                  = model * point_A4 ;
        point_B4                  = model * point_B4 ;
        point_C4                  = model * point_C4;
        
        point_A[0] = point_A4[0];
        point_A[1] = point_A4[1];
        point_A[2] = point_A4[2];
        point_B[0] = point_B4[0];
        point_B[1] = point_B4[1];
        point_B[2] = point_B4[2];
        point_C[0] = point_C4[0];
        point_C[1] = point_C4[1];
        point_C[2] = point_C4[2];


        Vector3f point_origin = ray.origin;
        Vector3f direction    = ray.direction;

        Vector3f A_sub_B = point_A - point_B;
        Vector3f A_sub_C = point_A - point_C;

        Matrix3f matrix_solve = Matrix3f::Identity();

        matrix_solve.col(0)   = direction;
        matrix_solve.col(1)   = A_sub_B;
        matrix_solve.col(2)   = A_sub_C;


        if (matrix_solve.determinant() == 0)//平行
            continue;
        
        Vector3f x_solve = matrix_solve.inverse() * (point_A - point_origin);

        if (x_solve[0] > 0 && x_solve[1] > 0 && x_solve[2] > 0 && x_solve[0] < 1 &&  x_solve[1] < 1 && x_solve[2] < 1) 
        {
            Vector3f x               = x_solve[0] * point_A + x_solve[1] * point_B + x_solve[2] * point_C;
            float t_temp   = (x - point_origin)[0] / direction[0];  
            if (t_temp > eps)
            {
                    
                if (result.t > t_temp) 
                {
                     result.barycentric_coord = x_solve;
                     result.face_index        = i;
                     result.t                 = t_temp;
                }
            }
        } 
        // Vertex a, b and c are assumed to be in counterclockwise order.
        // Construct matrix A = [d, a - b, a - c] and solve Ax = (a - origin)
        // Matrix A is not invertible, indicating the ray is parallel with the triangle.
        // Test if alpha, beta and gamma are all between 0 and 1.
    }
    // Ensure result.t is strictly less than the constant `infinity`.
    if (result.t - infinity < -eps) {
        return result;
    }
    return std::nullopt;
}
