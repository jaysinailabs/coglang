# CogLang Quickstart v1.1.0

**状态**：稳定发布伴随文档
**适用对象**：第一次接触 CogLang 的使用者、实现者  
**覆盖范围**：只覆盖 `Baseline` 中最常见、最稳定的写法  
**不覆盖**：`Reserved / Experimental` 的完整能力、扩展 operator 的显式限定名、宿主桥接 / 写意图 / 持久化后端细节

---

## 0. 这份文档解决什么问题

把这份文档当作第一次上手的 first-pass guide。

它只回答三个实际问题：

1. 第一次写 CogLang 时，应该先学哪些模式
2. 什么写法现在可以依赖，什么写法现在不要碰
3. 写出第一个合法表达式后，下一步应去哪里看权威定义

正式语义和配套边界分别见：

- **完整语义与冻结口径**：看 `CogLang_Specification_v1_1_0_Draft.md`
- **Profile / capability 边界**：看 `CogLang_Profiles_and_Capabilities_v1_1_0.md`
- **可执行样例与回归约束**：看 `CogLang_Conformance_Suite_v1_1_0.md`
- **独立安装与发布试用路径**：看 `CogLang_Standalone_Install_and_Release_Guide_v0_1.md`

如果你想先确认已安装包和对外公开建议使用的最小入口是否可用，可以直接运行：

```powershell
coglang info
coglang release-check
coglang parse 'Equal[1, 1]'
coglang validate 'Equal[1, 1]'
coglang execute 'Equal[1, 1]'
coglang manifest
coglang vocab
coglang examples
coglang demo
```

如果要运行 `doctor`、`smoke` 和随包 conformance checks，需要先安装 development extra，让 `pytest` 可用：

```powershell
pip install "coglang[dev]"
coglang doctor
coglang smoke
coglang conformance smoke
```

在当前稳定发布口径下，`release-check` 应通过；如果失败，通常意味着已安装包或发布元数据不完整。

---

## 1. Why CogLang Exists

先把 `CogLang` 当作一句话来理解：

`CogLang` 是一个 **graph-first expression language**，它被设计成更容易由语言模型生成，并在带审计边界的宿主契约下执行。

它当前明确坚持的几项设计选择是：

1. 采用稳定的 `M-expression / canonical text` 形态，而不是依赖更自由的表面语法。
原因是：先保证可解析性、可规范化和生成稳定性，再谈更花哨的写法。
2. 把错误当作值，而不是把求值失败默认做成异常中断。
原因是：在 AI 驱动的图操作里，部分失败和局部不可得是常态，不是例外。
3. 把 `profile / capability` 放进语言边界附近，而不是留到宿主之外再猜。
原因是：扩展与宿主都应显式声明“需要什么”，让宿主能在执行前拒绝不安全或不适用的动作。

它同样有明确的非目标：

- 它不是通用编程语言
- 它不是 schema definition language
- 它也不试图替代其他图查询语言在各自原生场景中的用途

如果你要的是成熟通用语言生态、完整应用框架或某个特定系统的原生查询体验，这份 Quickstart 不是那类入口。

---

## 2. 最小心智模型

第一次上手时，先记住 5 件事：

1. CogLang 是**图优先工作语言**。最先该学的是查询、条件、追踪，不是扩展语法。
2. 你平时写的是 **canonical text**。`readable render` 只是更适合人读的展示形式，不是另一门语法。
3. `Baseline` 是普通使用者入口。`Reserved` 不是默认可依赖能力。
4. `Create / Update / Delete` 冻结的是**语言级写意图**。它们不等于“执行器直接写某个持久化后端”。
5. 扩展 operator 的显式限定名不属于首批可教学语法。第一次上手不要依赖它。

---

## 3. 例子里默认假设的最小图谱

下面的例子默认有一个最小示例图谱：

- `einstein`
  `type = Entity`
  `category = "Person"`
  `label = "Einstein"`
- `tesla`
  `type = Entity`
  `category = "Person"`
  `label = "Tesla"`
- `ulm`
  `type = Entity`
  `category = "City"`
  `label = "Ulm"`
- 一条边：
  `einstein -[born_in]-> ulm`

这个假设与 conformance suite 的基础样例一致，只是把阅读时常用的字段显式写出来。

---

## 4. 第一批应学会的 4 类表达式

### 4.1 取字段

```text
Get["einstein", "label"]
```

期望返回：

```text
"Einstein"
```

这类写法适合先建立“节点 ID + 属性键 -> 值”的最小感觉。

### 4.2 查节点

```text
Query[n_, Equal[Get[n_, "category"], "Person"]]
```

期望返回：

```text
List["einstein", "tesla"]
```

这里先只学两件事：

- `n_` 是绑定变量
- `Query` 返回的是结果列表，不是自动入图对象

### 4.3 条件分流

```text
IfFound[Traverse["einstein", "born_in"], x_, x_, "unknown"]
```

期望返回：

```text
List["ulm"]
```

不要把 `IfFound` 理解成“空列表就走 else”。

冻结口径如下：

- `NotFound[]` 会走 `else`
- 自动传播错误值也会走 `else`
- `List[]` 不会自动改走 `else`

如果你需要把某一步产出的值继续传给下一步，`v1.1.0` 的官方写法就是 `IfFound[expr, v_, thenExpr, elseExpr]` 这种 bind-and-continue 模式；不要指望 `Do` 自动保留中间值。

### 4.4 加追踪

```text
Trace[Traverse["einstein", "born_in"]]
```

期望返回：

```text
List["ulm"]
```

并且：

- 语义返回值与不加 `Trace` 时相同
- trace / observer 中会出现对应执行事件

这类写法很重要，因为它能让你在不改变求值结果的前提下看到执行痕迹。

---

## 5. 第一批最常见的误区

### 5.1 不要把业务分类写进公开 `type`

下面这种旧写法现在不应继续教：

```text
Create["Entity", {"id": "tesla_02", "type": "Person"}]
```

原因不是“Person 不重要”，而是：

- 公开节点 `type` 只保留给 `Entity / Concept / Rule / Meta`
- 业务分类应进入其他字段，例如 `category`

### 5.2 不要把 `Reserved` 当成默认生产能力

`Explain`、`Inspect` 已有冻结签名和默认失败形态，但它们仍不是普通使用者的默认入口。

第一批表达式应先依赖：

- `Get`
- `Query`
- `Traverse`
- `If`
- `IfFound`
- `Trace`
- `Assert`

### 5.3 不要把扩展限定名当成现成语法

规范现在只冻结了“允许存在显式限定名称”这件事，没有冻结普通用户可写的具体分隔符。

这意味着：

- 实现者可以为扩展预留这项能力
- 普通使用者不应把它当作稳定语法来学

### 5.4 不要把语言级写意图误解成直接写权

你可以学：

```text
Create["Entity", {"id": "tesla_01", "label": "Tesla"}]
```

但你不应从这条语句反推出：

- 执行器一定直接写某个固定后端
- 不存在 `WriteBundle` 或 owning-module 代理链
- 语言返回值就等于架构提交对象

语言层冻结的是表达式语义；架构层冻结的是提交路径。

这也不意味着执行器“什么都不用做”。在 `v1.1.0` 冻结边界下，宿主运行时负责预分配 ID、形成 `WriteBundleCandidate` 或等价中间写入请求，并把提交结果映射回语言级返回值。

---

## 6. 第一次上手时，哪些先不要碰

如果你的目标只是“学会写第一批合法表达式”，先不要从这些地方开始：

- `Explain`
- `Inspect`
- 非默认 `Query.mode`
- 查询 `cost / gain` 元推理接口
- extension-backed operator
- 扩展 operator 的显式限定名

这些能力属于第二批主题，不属于第一批心智模型。

---

## 7. 学完这份后应该去哪

如果你已经理解了上面的 4 类表达式，按角色继续阅读：

### 7.1 普通使用者

接下来读：

1. `CogLang_Specification_v1_1_0_Draft.md`
   先读 `四层表示模型`、`Core operators`、`错误模型`
2. `CogLang_Conformance_Suite_v1_1_0.md`
   重点看 `GE-003`、`GE-004`、`GE-006`、`GE-007`、`GE-021`、`GE-022`

### 7.2 实现者

接下来读：

1. `CogLang_Specification_v1_1_0_Draft.md`
2. `CogLang_Conformance_Suite_v1_1_0.md`
3. `CogLang_Migration_v1_0_2_to_v1_1_0.md`

---

## 8. 一句话总结

第一次上手时，把 CogLang 当成：

**一个图优先、先学 `Baseline`、先学查询与条件、把扩展与架构细节留到后面的工作语言。**
