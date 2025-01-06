#include <iostream>
#include <cmath>
#include <algorithm>
#include <utility>
#include <fstream> 
using namespace std;

typedef pair<pair<long double,long double>,pair<long double,long double>> ppld;
const long double eps = 5e-6;
const long limit = 10000;
const long double alpha = 0.1;
const long double beta = 0.7;
long k_cnt = 0;

long double gamma = 0.01;

pair<long double, long double> x;

ofstream outputFile("newton.csv");
long double lambda;
pair<long double, long double> dt;

pair<long double, long double> delta(pair<long double, long double> x)
{
    return make_pair(exp(x.first + 3 * x.second - 0.1) + exp(x.first - 3 * x.second - 0.1) - exp(-x.first - 0.1), 3 * exp(x.first + 3 * x.second - 0.1) - 3 * exp(x.first - 3 * x.second - 0.1));;
}

pair<long double, long double> operator-(pair<long double, long double> x, pair<long double, long double> y)
{
    return make_pair(x.first - y.first, x.second - y.second);
}

pair<long double, long double> operator+(pair<long double, long double> x, pair<long double, long double> y)
{
    return make_pair(x.first + y.first, x.second + y.second);
}

pair<long double, long double> operator*(long double x, pair<long double, long double> y)
{
    return make_pair(x * y.first, x * y.second);
}

long double operator*(pair<long double, long double> x, pair<long double, long double> y)
{
    return x.first * y.first + x.second * y.second;
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

pair <long double,long double> operator*(ppld x, pair<long double,long double> y)
{
    return make_pair(x.first * y, x.second * y);
}

long double f(pair<long double, long double> x)
{
    return exp(x.first + 3 * x.second - 0.1) + exp(x.first - 3 * x.second - 0.1) + exp(-x.first - 0.1);
}

ppld d2f(pair<long double,long double> x)
{
    long double ddx = delta(x).second;
    return make_pair(make_pair(f(x), ddx), make_pair(ddx, 9 * exp(x.first + 3 * x.second - 0.1) + 9 * exp(x.first - 3 * x.second - 0.1)));
}

ppld operator/(ppld x, long double y)
{
    return make_pair(make_pair(x.first.first / y, x.first.second / y), make_pair(x.second.first / y, x.second.second / y));;
}

ppld operator*(ppld x, long double y)
{
    return make_pair(make_pair(x.first.first * y, x.first.second * y), make_pair(x.second.first * y, x.second.second * y));;
}

ppld operator-(ppld x)
{
    return make_pair(make_pair(-x.first.first, -x.first.second), make_pair(-x.second.first, -x.second.second));
}


bool stop_time()
{
    if (k_cnt > limit)
        return false;
    ppld d2x = d2f(x);
    pair<long double, long double> dx = delta(x);
    d2x = make_pair(make_pair(d2x.second.second, -d2x.second.first), make_pair(-d2x.first.second, d2x.first.first)) / (d2x.first.first * d2x.second.second - d2x.first.second * d2x.second.first);
    
    dt = -d2x * dx;
    lambda = dt * (d2f(x) * dt);
    if (eps >= lambda / 2)
        return false;
    return true;
}

long double solve_t()
{
    long double t = 1;
    while (f(x + t * dt) > f(x) - alpha * t * lambda)
        t = beta * t;
    return t;
}
int main()
{

    x.first = 3;
    x.second = 3;
    while (stop_time())
    {
        long double t_k = solve_t();
        outputFile << k_cnt << "," << f(x) << endl;
        x = x + t_k * dt;
        k_cnt++;
    }
    outputFile.close();
    cout << "当alpha = " << alpha << ", beta = " << beta << " 时；" << endl;
    cout << "迭代次数k_cnt = " << k_cnt << endl;
    cout << "x = [ " << x.first << " , " << x.second << " ];" << endl;
    cout << "f（x) = " << f(x) << endl;
    return 0;
}