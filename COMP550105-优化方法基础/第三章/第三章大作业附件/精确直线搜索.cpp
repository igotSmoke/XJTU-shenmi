#include <iostream>
#include <cmath>
#include <algorithm>
#include <utility>

using namespace std;

const long double eps = 5e-6;
const long limit = 10000;
const long double e = 2.71828182;
const long double alpha = 0.5;
const long double beta = 0.9;
long k_cnt = 0;

long double gamma = 0.01;

pair<long double, long double> x;
pair<long double, long double> dx;

pair<long double, long double> delta(pair<long double, long double> x)
{
    return make_pair(exp(x.first + 3 * x.second - 0.1) + exp(x.first - 3 * x.second - 0.1) - exp(-x.first - 0.1), 3 * exp(x.first + 3 * x.second - 0.1) - 3 * exp(x.first - 3 * x.second - 0.1));;
}

pair<long double, long double> operator-(pair<long double, long double> x, pair<long double, long double> y)
{
    return make_pair(x.first - y.first, x.second - y.second);
}
pair<long double, long double> operator*(long double x, pair<long double, long double> y)
{
    return make_pair(x * y.first, x * y.second);
}

long double square(pair<long double, long double> y)
{
    return y.first * y.first + y.second * y.second;
}

long double solve_fan(pair<long double, long double> x)
{
    long double sqr_sum = x.first * x.first + x.second * x.second;

    return sqrtl(sqr_sum);
}



long double f(pair<long double, long double> x)
{
    return exp(x.first + 3 * x.second - 0.1) + exp(x.first - 3 * x.second - 0.1) + exp(-x.first - 0.1);
}

bool stop_time()
{
    if (k_cnt > limit)
        return false;
    dx = delta(x);
    if (eps >= solve_fan(dx))
        return false;
    return true;
}

long double solve_t()
{
    long double t = 1;
    while (f(x - t * dx) > f(x - (t * beta) * dx)  || f(x - t * dx) > 100000000000)
        t = beta * t;
    return t;
    /*long double t = 1;
    while (f(x - t * dx) > f(x) - alpha * t * square(dx))
        t = beta * t;
    return t;*/
    ;
    
}
int main()
{

    x.first = 4;
    x.second = 4;
    while (stop_time())
    {
        long double t_k = solve_t();
        x = x - t_k * dx;
        k_cnt++;
    }
    
    cout << "当alpha = " << alpha << ", beta = " << beta << " 时；" << endl;
    cout << "迭代次数k_cnt = " << k_cnt << endl;
    cout << "x = [ " << x.first << " , " << x.second << " ];" << endl;
    cout << "f（x) = " << f(x) << endl;
    return 0;
}