### 等式约束凸优化问题求解方法总结

目标问题为：

\[
\min f(x)\ s.t.\ Ax = b
\]

其中，$f : \mathbb{R}^n \to \mathbb{R}$ 为二次连续可微凸函数，$A \in \mathbb{R}^{p \times n}$，且 $rank(A) = p < n$。

#### 1. 消除方法
- 通过构造矩阵 $F \in \mathbb{R}^{n \times (n-p)}$， $R(F) = N(A)$，将优化问题的变量 $x$ 转换为无约束优化问题。
- 对于任意 $z \in \mathbb{R}^{n-p}$，$x = Fz + \hat{x}$，其中 $\hat{x}$ 是满足 $A \hat{x} = b$ 的特解。
- 将优化问题变为：
  
  \[
  \min f(Fz + \hat{x})
  \]

- 使用无约束优化方法求解该问题。

#### 2. 对偶方法
- 等式约束的凸优化问题，在满足可行解条件时，必然满足 Slater 条件，因此对偶问题存在强对偶性。
- 构造拉格朗日对偶函数：

  \[
  g(v) = \inf_x \left( f(x) + v^T(Ax - b) \right)
  \]

  根据slater条件，得到对偶问题最优值 $d^* = p^*$。再求解：

  \[
  g(v) = \min_x \left( f(x) + (v^*)^T(Ax - b) \right)
  \]
  求解对偶问题：

  \[
  \max_v g(v)
  \]
  获取最优原始解 $x^*$。

#### 3. 牛顿方法
##### 3.a 可行初始点的牛顿方法
- 在可行初始点使用牛顿方向进行优化，修改后的牛顿步为：

  \[
  \begin{bmatrix}
  \nabla^2 f(x) & A^T \\
  A & 0
  \end{bmatrix}
  \begin{bmatrix}
  d_x \\
  w
  \end{bmatrix}
  = - \begin{bmatrix}
  \nabla f(x) \\
  0
  \end{bmatrix}
  \]

- 停止准则使用牛顿减少量 $\lambda(x) = (d_x^T \nabla^2 f(x) d_x)^{1/2}$。

- 使用回溯直线搜索和迭代方法求解。

##### 3.b 不可行初始点的牛顿方法
- 在不可行初始点同时优化原始变量 $x$ 和对偶变量 $v$，使用原对偶残差：

  \[
  r\left( \begin{array}{c} x \\ v \end{array} \right) = \begin{bmatrix} \nabla f(x) + A^T v \\ Ax - b \end{bmatrix}
  \]

- 牛顿方向为：

  \[
  \begin{bmatrix}
  \nabla^2 f(x) & A^T \\
  A & 0
  \end{bmatrix}
  \begin{bmatrix}
  d_x \\
  d_v
  \end{bmatrix}
  = - r\left( \begin{array}{c} x \\ v \end{array} \right)
  \]

- 使用回溯直线搜索对残差进行回溯，回溯停止准则为：

  \[
  \| r\left( \begin{array}{c} x + t d_x \\ v + t d_v \end{array} \right) \|_2 \leq (1 - \alpha t) \| r\left( \begin{array}{c} x \\ v \end{array} \right) \|_2
  \]

- 迭代更新直到收敛。

### 相互联系：
1. **牛顿方法与消除方法的关系**：
   - 由于仿射不变性，等式约束牛顿方法和通过消除方法变为无约束问题的牛顿方法是等价的。
   - 通过消除方法将约束转换为无约束问题后，牛顿步径是对应的。

2. **不可行初始点牛顿方法与对偶方法的关系**：
   - 不可行初始点的牛顿方法不仅优化原始变量 $x$，还优化对偶变量 $v$。
   - 最终收敛得到的对偶变量 $v^*$ 与对偶方法中求得的最优对偶变量一致，满足强对偶性条件。

通过这三种方法可以有效地求解等式约束的凸优化问题，根据初始条件的不同选择相应的求解策略。
