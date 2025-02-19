Matrix4f Object::model()
{
    //根据物体的center,rotation和scaling三个属性计算出model matrix，其中center scaling 均为Vector3f，rotation则需转化为欧拉角
    auto [x_angle, y_angle, z_angle] = quaternion_to_ZYX_euler(rotation.w(), rotation.x(), rotation.y(), rotation.z());
    x_angle = radians(x_angle);
    y_angle = radians(y_angle);
    z_angle = radians(z_angle);

    Matrix4f scalingMatrix = Matrix4f::Identity();
    scalingMatrix(0, 0)    = scaling.x();
    scalingMatrix(1, 1)    = scaling.y();
    scalingMatrix(2, 2)    = scaling.z();//缩放矩阵完成

    Matrix4f rx4f = Matrix4f::Identity();
    rx4f(1, 1)    = cos(x_angle);
    rx4f(1, 2)    = -1 * sin(x_angle);
    rx4f(2, 1)    = sin(x_angle);
    rx4f(2, 2)    = cos(x_angle);

    Matrix4f ry4f = Matrix4f::Identity();
    ry4f(0, 0)    = cos(y_angle);
    ry4f(0, 2)    = sin(y_angle);
    ry4f(2, 0)    = -1 * sin(y_angle);
    ry4f(2, 2)    = cos(y_angle);

    Matrix4f rz4f = Matrix4f::Identity();
    rz4f(0, 0)    = cos(z_angle);
    rz4f(0, 1)    = -1 * sin(z_angle);
    rz4f(1, 0)    = sin(z_angle);
    rz4f(1, 1)    = cos(z_angle);

    Matrix4f rotationMatrix = rx4f * ry4f * rz4f;

    Matrix4f translationMatrix = Matrix4f::Identity();
    translationMatrix(0, 3)    = center.x();
    translationMatrix(1, 3)    = center.y();
    translationMatrix(2, 3)    = center.z();

    Matrix4f modelMatrix = Matrix4f::Identity();
    modelMatrix          = translationMatrix * rotationMatrix * scalingMatrix;

    return modelMatrix;
}