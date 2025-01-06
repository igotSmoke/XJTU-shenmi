#include <iostream>
#include <vector>
#include <random>
#include <fstream>
#include <cmath>
#include <Eigen/Dense>

using namespace std;
using namespace Eigen;

// 全局输出流对象
ofstream output("output.txt");

double alpha = 0.3;
double beta = 0.8;
double tol = 1e-6;

// 随机生成满秩矩阵 A
MatrixXd generateFullRankMatrix(int rows, int cols) {
    MatrixXd A = MatrixXd::Random(rows, cols);
    while (A.fullPivLu().rank() != rows) {
        A = MatrixXd::Random(rows, cols);
    }
    return A;
}

// 生成随机正向量 \(\hat x\)
VectorXd generatePositiveVector(int size, double lower = 0.1, double upper = 0.9) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(lower, upper);

    VectorXd vec(size);
    for (int i = 0; i < size; ++i) {
        vec[i] = dis(gen);
    }
    return vec;
}

double f(const VectorXd& x) {
    double result = 0.0;
    for (int i = 0; i < x.size(); ++i) {
        if (x[i] > 0) {
            result += x[i] * log(x[i]);
        }
    }
    return result;
}

VectorXd gradient(const VectorXd& x) {
    return x.array().log().matrix() + VectorXd::Ones(x.size());
}

MatrixXd hessian(const VectorXd& x) {
    return x.cwiseInverse().asDiagonal();
}

VectorXd rxv(const VectorXd& x, const VectorXd& v, const MatrixXd& A, const VectorXd& b) {
    VectorXd primalResidual = gradient(x) + A.transpose() * v;
    VectorXd dualResidual = A * x - b;

    VectorXd residual(primalResidual.size() + dualResidual.size());
    residual << primalResidual, dualResidual;

    return residual;
}

// 标准 Newton 方法
VectorXd standardNewton(const MatrixXd& A, const VectorXd& b, VectorXd x0) {
    VectorXd x = x0;
    int k = 0;
    while (k <= 1000) {
        MatrixXd H = hessian(x);
        int n = H.rows();
        int m = A.rows();

        MatrixXd K(n + m, n + m);
        K.block(0, 0, n, n) = H;
        K.block(0, n, n, m) = A.transpose();
        K.block(n, 0, m, n) = A;
        K.block(n, n, m, m) = MatrixXd::Zero(m, m);

        VectorXd rhs(n + m);
        rhs.head(n) = -gradient(x);
        rhs.tail(m) = VectorXd::Zero(m);

        VectorXd solution = K.fullPivLu().solve(rhs);
        VectorXd d = solution.head(n);

        double lambda = d.transpose() * hessian(x) * d;
        if (0.5 * lambda <= tol) {
            output << "Optimal x (Standard Newton):" << endl << x.transpose() << endl;
            output << " k = " << k << endl;
            output << " p* = " << f(x) << endl;
            return x;
        }

        double t = 1;
        while (f(x + t * d) > f(x) - alpha * t * lambda) {
            t = beta * t;
            if (t < 1e-10) break;
        }

        x = x + t * d;
        k++;
    }
    output << "Standard Newton did not converge." << endl;
    return x;
}

// 不可行初始点 Newton 方法
VectorXd infeasibleNewton(const MatrixXd& A, const VectorXd& b, VectorXd x0, VectorXd v0) {
    VectorXd x = x0;
    VectorXd v = v0;
    int k = 0;
    while (k <= 100) {
        if (rxv(x, v, A, b).norm() <= tol) {
            output << "Optimal x (Infeasible Newton):" << endl << x.transpose() << endl;
            output << " k = " << k << endl;
            output << " p* = " << f(x) << endl;
            return x;
        }

        MatrixXd H = hessian(x);
        int n = H.rows();
        int m = A.rows();

        MatrixXd K(n + m, n + m);
        K.block(0, 0, n, n) = H;
        K.block(0, n, n, m) = A.transpose();
        K.block(n, 0, m, n) = A;
        K.block(n, n, m, m) = MatrixXd::Zero(m, m);

        VectorXd rhs(n + m);
        rhs.head(n) = -gradient(x) - A.transpose() * v;
        rhs.tail(m) = -A * x + b;

        VectorXd solution = K.fullPivLu().solve(rhs);
        VectorXd dx = solution.head(n);
        VectorXd dv = solution.tail(m);

        double t = 1;
        while (rxv(x + t * dx, v + t * dv, A, b).norm() > (1 - alpha * t) * rxv(x, v, A, b).norm()) {
            t = beta * t;
            if (t < 1e-10) break;
        }

        x = x + t * dx;
        v = v + t * dv;
        k++;
    }
    output << "Infeasible Newton did not converge." << endl;
    return x;
}

// 对偶 Newton 方法
VectorXd dualNewton(const MatrixXd& A, const VectorXd& b, VectorXd x0, int maxIter = 100, double tol = 1e-6) {
    int n = x0.size();
    int p = A.rows();
    VectorXd v = VectorXd::Zero(p);
    int iter = 0;
    for (iter = 0; iter < maxIter; ++iter) {
        VectorXd exp_term = (-1.0 * VectorXd::Ones(n) - A.transpose() * v).array().exp().matrix();
        VectorXd grad = b - A * exp_term;
        MatrixXd hess = A * exp_term.asDiagonal() * A.transpose();

        VectorXd dv = hess.fullPivLu().solve(-grad);

        if (dv.norm() < tol) break;

        v += dv;
    }

    VectorXd x = (-1.0 * VectorXd::Ones(n) - A.transpose() * v).array().exp();
    output << "Optimal x (Dual Newton):" << endl << x.transpose() << endl;
    output << " k = " << iter << endl;
    output << " p* = " << f(x) << endl;
    return x;
}

int main() {
    int n = 100, p = 30;
    MatrixXd A = generateFullRankMatrix(p, n);
    VectorXd x_hat = generatePositiveVector(n);
    VectorXd b = A * x_hat;

    output << "Matrix A (p x n):" << endl << A << endl;
    output << "Feasible point x_hat:" << endl << x_hat.transpose() << endl;
    output << "b = A * x_hat:" << endl << b.transpose() << endl;

    VectorXd x_standard = standardNewton(A, b, x_hat);
    VectorXd x_infeasible = infeasibleNewton(A, b, x_hat, VectorXd::Ones(p));
    VectorXd x_dual = dualNewton(A, b, x_hat);

    output.close();
    return 0;
}