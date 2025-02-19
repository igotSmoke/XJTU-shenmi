Matrix4f Camera::projection()
{
    const float fov_y = radians(fov_y_degrees);
    const float top   = (target - position).norm() * std::tan(fov_y / 2.0f);
    const float right = top * aspect_ratio;

    Matrix4f projection = Matrix4f::Zero();
    // 使用平行投影时，用户并不能从画面上直观地感受到相机的位置，
    // 因而会产生近处物体裁剪过多的错觉。为了产程更好的观察效果，
    // 这里没有使用相机本身的 near 而是取 near = -far 来让相机能看到“背后”的物体。
    projection(0, 0) = 1.0f / right;
    projection(1, 1) = 1.0f / top;
    projection(2, 2) = -1.0f / far;
    projection(2, 3) = 0.0f;
    projection(3, 3) = 1.0f;

    /*
position	相机位置（观察点）
target	相机指向的目标点
near_plane	可视范围近平面到观察坐标系原点的距离（正值）
far_plane	可视范围远平面到观察坐标系原点的距离（正值）
fov_y_degrees	高度方向（Y 方向）的视角大小，单位是角度
aspect_ratio	宽高比，即视角的宽度 / 高度
*/

    float pov_y = radians(fov_y_degrees);
    pov_y       = pov_y / 2;
    float h = 2 * near * tan(pov_y);

    Matrix4f matPersp1 = Matrix4f::Identity();
    matPersp1(0, 0)    = 2 * near / ( h * aspect_ratio);
    matPersp1(1, 1)    = 2 * near / h;
    matPersp1(2, 2)    = (near + far) / (near - far);
    matPersp1(2, 3)    = 2 * near * far / (near - far);
    matPersp1(3, 2)    = -1;
    matPersp1(3, 3)    = 0;


    return matPersp1;
}