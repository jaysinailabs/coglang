# CogLang 语言规范

**版本：v1.1.0-pre**
**状态：预发布态（文件名暂保留 `Draft` 以兼容既有引用）**
**定位：英文主规范的中文伴随译本；若与英文版、可执行 conformance 或实现测试不一致，以英文版与可执行材料为准**

---

## 0. 本文档的角色

本中文译本对应 CogLang `v1.1.0-pre` 的预发布主规范，用于辅助阅读以下内容：

- `v1.0.2` 已冻结的核心语法、求值、错误语义
- 当前架构边界下对扩展机制、元推理、可观测性、查询接口、规则桥接的要求
- 需要在语言层提前声明、但不由本版主文直接冻结实现细节的保留能力

本文档已不再作为“章节骨架草案”使用。对当前阶段而言，它应被视为英文主规范的中文伴随译本，用于辅助理解：

- 语言表面、求值语义、错误模型与表达式级可观测性的预发布规范内容
- companion docs、conformance、迁移文档与宿主集成引用时的主依据；若有冲突，以英文主规范和可执行材料为准
- 后续 `Reserved / Experimental` 收口与实现对齐的判断基线

---

## 1. 规范地位与版本策略

### 1.1 文档性质

本规范区分两类内容：

- **Normative**：实现、测试、训练数据、兼容性判断必须遵守
- **Informative**：设计动机、示例、非约束性解释、未来方向

正文中应显式使用以下术语：

- `MUST`
- `SHOULD`
- `MAY`
- `RESERVED`
- `EXPERIMENTAL`

若正文中的 Informative 描述与 Normative 规则冲突，以 Normative 规则为准。

### 1.1.1 兼容性表面

CogLang 的兼容性不是单一维度，而是至少包含以下 5 个表面：

1. **Parser surface**：文本能否被解析为 AST
2. **Validator surface**：表达式是否是合法的 CogLang 程序
3. **Execution surface**：执行器对语义和错误行为的实现是否一致
4. **Rendering surface**：可读渲染与 trace 展示是否稳定
5. **Canonical serialization surface**：规范序列化是否仍保持稳定

规范中的兼容性声明 **SHOULD** 明确指出作用表面。

若未特别说明：

- 对 `Core` 能力，兼容性默认至少指不破坏 `parser / validator / execution` 三个表面
- 若某项变更会影响 `rendering` 或 `canonical serialization` 表面，正文 **MUST** 显式写出

### 1.1.2 计算范围与语言身份

`CogLang` 在 `v1.1.0` 中的定位 **MUST** 被理解为：

- 图优先执行语言
- AI 专用语义接口
- 支持程序性组合，但不以通用编程语言为目标

本规范只冻结：

- 语言表面与 canonical serialization
- parser / validator / execution 的最小一致性要求
- 表达式级可观测性与扩展边界

本规范**不**直接冻结：

- 应用侧交换对象的 canonical 地位或字段职责
- 持久化后端的物理存储形态
- 消息或任务分发协议的分类方式
- 规则候选、发布、回滚的完整生命周期对象模型

这里的“图优先”指：

- 核心公开对象模型围绕图谱节点、边、规则对象及其可审计结果展开
- 控制流、结构值、组合能力的引入，首先服务于图查询、图更新、规则触发、验证前表示与可观测执行

这里的“支持程序性组合”指：

- `If / Do / ForEach / Compose / List / Dict` 等能力可用于组织局部执行过程
- 这些能力的主要目的，是支撑图语义主链，而不是把 `CogLang` 扩张为面向人类手写的通用脚本语言

因此，若某项新增能力主要服务于：

- 面向人类手写舒适度的语法便利
- 与传统通用语言表面对齐
- 与图语义主链无直接关系的大规模通用运行时能力

则该能力 **SHOULD NOT** 在没有明确图优先理由的前提下直接进入 `Core`。

### 1.2 版本演化原则

`v1.0.2` 的冻结仅适用于 P0 依赖期，不构成永久冻结。

`v1.1.0` 的目标是：

- 保持 `v1.0.2` 核心语义稳定
- 引入当前阶段所需的结构化扩展点
- 为 Reserved / Experimental 能力建立清晰边界

`v1.1.0` 的首要目标不是扩大 CogLang 的表面语法自由度，而是让：

- 语言语义
- 扩展边界
- 人类可读界面
- 执行器 / runtime bridge / trace 的接口契约

在同一份规范里具有一致的判定标准。

### 1.2.1 版本号规则

本规范采用以下版本语义：

- `v1.0.x`：勘误版本；仅允许兼容性修正、消歧义、遗漏补充
- `v1.x`：向后兼容扩展；允许新增 `Reserved` / `Experimental` / 新 `Core` 能力，但不得破坏既有 `Core`
- `v2.x`：允许破坏性变更；必须附带迁移文档与兼容性说明

### 1.3 三层特性体系

CogLang 特性分为三层：

| 层级 | 含义 | 兼容性承诺 |
|------|------|------------|
| `Core` | 已冻结的核心语言能力 | 名称与语义均稳定 |
| `Reserved` | 已占位、可被调用、但语义或实现未完整冻结 | 名称稳定，语义可收敛 |
| `Experimental` | 探索中能力 | 名称与语义均可能调整 |

### 1.4 特性晋升规则

#### `Experimental -> Reserved`

某项能力从 `Experimental` 晋升到 `Reserved`，至少必须满足：

- 名称冻结：operator 名称或抽象能力名称固定
- 所属层固定：明确是 `language / executor / runtime_bridge / observability / adapter` 中哪一层
- 最小签名固定：参数个数、参数角色、默认错误行为明确
- 验证阶段失败形式与运行阶段默认失败行为均明确
- trace 策略明确：是否需要进入推理轨迹，最小记录字段是什么

#### `Reserved -> Core`

某项能力从 `Reserved` 晋升到 `Core`，至少必须满足：

- Normative 语义完整，不依赖“由实现者自行判断”的关键分支
- 至少一份参考实现通过一致性测试
- 对 parser / validator / executor / readable render 的影响均已落地
- 错误语义、权限边界、可观测性字段均已冻结
- 训练与数据生成链路已有稳定 canonical 写法

#### Breaking Change 窗口

以下变更视为 breaking change：

- 已有 `Core` operator 的签名变化
- `Core` 错误表达式结构变化
- canonical 序列化变化
- 已冻结 Head 的名称语义变化
- readable render 中导致人类定位失效的结构变化

breaking change 仅允许发生在：

- `-draft` 阶段
- 且必须同步更新迁移说明与 golden examples

对已发布的非 draft 版本，任何 breaking change 都必须伴随新版本号和迁移文档。

#### 与伴随资产的联动要求

以下内容一旦进入 `Reserved` 或 `Core`，必须同步更新：

- conformance suite
- operator catalog
- migration 文档
- rendering / UI 契约
- 如影响训练格式，则更新训练数据规范

---

## 2. 术语与一致性约定

本节定义正文中的稳定术语。

| 术语 | 含义 |
|------|------|
| `expression` | 语法上的 CogLang 表达式 |
| `Head` | AST 中位于表达式首位、用于名称解析的符号名 |
| `operator head` | 以大写字母开头、可参与 operator 名称解析的 Head |
| `term head` | 以小写字母开头、用于结构化项或模式表示的 Head |
| `AST` | 解析后的内部结构化表示；执行语义的权威对象 |
| `canonical text` | 唯一规范序列化形式，用于训练数据、存储、回归测试 |
| `readable render` | 为人类展示而生成的稳定文本，不要求作为规范写法 |
| `transport envelope` | 为 trace、UI、跨组件传输而包装的结构化对象 |
| `primitive` | 不能从其他操作派生的核心操作 |
| `built-in` | 由执行器原生提供语义的操作；special-form 或原生类型分派只是常见实现方式，不是必要条件 |
| `shortcut` | 为降低生成难度而预置的常用模式 |
| `ABSTRACT` | 架构文中的模块/机制写法；除非版本迁移说明另有声明，当前语言表面的 canonical Head 仍记作 `Abstract` |
| `extension-backed operator` | 由注册表或外部 adapter 提供实现的 operator |
| `graph-read` | 读取图谱但不修改图谱的效果类别 |
| `graph-write` | 修改图谱、规则层或持久状态的效果类别 |
| `meta` | 对执行计划、成本、规则状态等元层对象进行操作 |
| `diagnostic` | 仅用于 trace、断言、诊断、渲染的效果类别 |
| `external` | 依赖外部插件、外部系统或外部知识源的效果类别 |
| `deterministic` | 在相同输入与相同状态下结果应完全一致 |
| `graph-state-dependent` | 结果依赖当前图谱状态 |
| `model-dependent` | 结果依赖模型或 learned component |
| `implementation-defined` | 规范允许实现决定细节，但必须文档化 |

除非特别声明：

- `Head` 指语法层的名称
- `operator` 指名称解析完成后可被调用的能力
- `operator head` 与 `term head` 共享同一应用式语法外形，但只前者进入默认 operator 解析流程

同一名称在不同运行时层可映射到不同的 operator 实现，但其 AST 中的 `Head` 仍是单一语法对象。

---

## 3. 表示层模型

### 3.1 四层表示

CogLang 的规范对象必须分为四层：

1. **AST / 内部语义对象**
2. **Canonical Text / 规范序列化**
3. **Readable Render / 人类可读展示**
4. **Transport Envelope / trace、UI、跨组件传输包装**

### 3.2 四层转换约束

#### `AST <-> Canonical Text`

`AST` 与 `canonical text` 之间必须满足无损 round-trip：

- `parse(canonical_text(expr)) == expr`
- `canonical_text(parse(text))` 必须产生唯一规范形式

此处“相等”指**结构相等**，忽略 source span、render hint 与 transport-only metadata。

若某种文本写法可被 parser 接受但不是 canonical 形式，pretty-printer 必须将其归一化为 canonical 形式。

#### `AST -> Readable Render`

`readable render` 的目标是帮助人类理解，而不是替代 canonical 形式。因此：

- `readable render` 不要求可直接反解析为同一 AST
- 但同一 AST 在同一 render profile 下必须得到稳定输出
- `readable render` 不得凭空引入 AST 中不存在的语义信息
- 若 readable render 被嵌入 trace 或 UI envelope，必须保留可追溯到原 AST 节点的定位信息

#### `AST -> Transport Envelope`

`transport envelope` 用于 UI、trace、跨组件通信。其最小职责是：

- 携带原始 AST 或可定位到 AST 的引用
- 携带 canonical text 或其引用
- 可选携带 readable render
- 携带与本次执行相关的 trace / source / capability / confidence 等辅助字段

`transport envelope` 不属于 CogLang 核心语法；它是运行时与展示层的结构化包装。

#### UI 降噪规则

面向人类展示时允许：

- 折叠长列表
- 隐藏默认值
- 展示结构摘要而非完整子树

但以下信息不得丢失：

- Head 名称
- 参数位置关系
- 错误类型
- 规则 / trace / source 的可追溯引用

### 3.3 CogLang 的语义对象

CogLang 的语义对象是图结构与 AST，不是 token 序列。

因此：

- 执行器与宿主运行时桥接层之间的权威交换对象应是 AST 或等价结构对象，而不是 prompt token 流
- token 顺序只属于序列化层，不反向决定图语义
- 面向 LLM 的 prompt 包装、`<|end_coglang|>` 等终止 token 不属于 CogLang 核心语义

本规范默认以下边界：

- **语言边界**：`AST`、canonical form、错误语义、operator 语义
- **渲染边界**：readable render、UI 展示、trace 可读摘要
- **运行时边界**：runtime bridge / host transport / adapter 的 envelope 字段和 capability 检查

若某项信息只属于运行时边界，则不应因其 UI 或 trace 需要而被强行提升为核心语法成分。

---

## 4. 词法与语法

### 4.1 词法规则

CogLang 的 `v1.1.0` canonical surface 只冻结最小词法集合，不为未来限定名语法预先占用具体分隔符。

#### 标识符与变量

- `operator head`：以大写字母开头，后跟字母、数字或 `_`，且不得以 `_` 结尾
- `term head` / `atom`：以小写字母开头，后跟字母、数字或 `_`，且不得以 `_` 结尾
- 命名变量：以字母开头，后跟字母、数字或 `_`，并以单个尾部 `_` 结束
- 匿名通配符：单独的 `_`

因此，`Traverse` 是合法 `operator head`，`f` 是合法 `term head`，`person_` 是合法命名变量，而 `Traverse_` 不是合法 `operator head`。

#### 字符串字面量

- 使用双引号包围
- canonical surface 至少支持 `\"` 与 `\\` 转义
- 换行、制表等额外转义序列可由实现支持，但 canonical serializer 必须稳定输出

#### 数字

- 支持十进制整数与十进制浮点数
- 不允许前导 `+`
- 整数 canonical form 不带小数点

#### 保留符号

`[ ] { } , : "`

这些符号分别用于：

- application 定界
- 字典字面量
- 参数分隔
- 键值分隔
- 字符串定界

#### 空白、换行与注释

- canonical text 中，除字符串字面量内部外，空白只承担分隔作用
- 多个空白字符不得影响 AST
- 注释不属于 `v1.1.0` 的 canonical surface

宿主工具若支持注释，只能把它作为非 canonical 输入便利；在进入 canonical serialization 与一致性测试前，注释必须被剥离

### 4.2 语法规则

`v1.1.0` 的最小 EBNF 如下：

```ebnf
expression      ::= application
                  | atom
                  | string_literal
                  | number_literal
                  | named_variable
                  | wildcard
                  | dict_literal ;

application     ::= head_symbol "[" [arguments] "]" ;
arguments        ::= expression { "," expression } ;

head_symbol      ::= operator_head | term_head ;
operator_head    ::= upper_letter { letter | digit | "_" } ;
term_head        ::= lower_letter { letter | digit | "_" } ;
atom             ::= term_head ;
named_variable   ::= identifier_core "_" ;
wildcard         ::= "_" ;
identifier_core  ::= letter { letter | digit | "_" } ;

dict_literal     ::= "{" [dict_entries] "}" ;
dict_entries     ::= dict_entry { "," dict_entry } ;
dict_entry       ::= string_literal ":" expression ;
```

补充约束：

- `operator head` 与 `term head` 在语法上都可形成 `application`
- 只有 `operator head` 默认参与 `§10` 的 operator 名称解析
- `term head` 与 `atom` 用于结构化项、模式、或数据项表示；它们是否可出现在某个参数位置，由外层 operator 的条目决定
- `True[]`、`False[]`、`NotFound[]` 等是零参数 `application`

这一定义显式修复了 `v1.0.2` 中“大写 Head 规则”与 `Unify[f[a], ...]` 这类结构化项示例之间的历史矛盾：小写 `term head` 合法，但它不是默认可执行 operator。

### 4.3 Canonical Form

canonical text 是单个 AST 的唯一规范序列化形式。

`v1.1.0` 冻结以下 canonical 规则：

1. `Head` 与 `[` 之间无空格
2. 参数之间使用 `, ` 分隔
3. application 始终显式写出方括号，零参数 application 也必须写成 `Head[]`
4. 字符串使用双引号；canonical serializer 必须稳定转义内部引号与反斜杠
5. 字典使用 JSON 风格 `{}`，冒号后一个空格，逗号后一个空格
6. 字典键按字典序稳定排序
7. canonical text 始终是单行

对于数字：

- 整数必须输出为不带小数点的十进制形式
- 非整数必须输出为实现可 round-trip 的稳定十进制形式

多行文本不是 canonical text。本规范对“多行顺序输入”的处理规则如下：

- 若宿主允许一段文本包含多个顶层表达式
- 它必须在进入 AST / validator 之前被显式降格为一个顺序容器
- 在 `v1.1.0` 的默认语义下，该顺序容器是 `Do[...]`

因此，多行是宿主输入便利，不是核心语法新增结构。

### 4.4 Readable Render

Readable Render 是面向人类的稳定展示，不要求是唯一写法，但必须可稳定生成。

推荐的基础折行规则如下：

- 单行表达式可直接显示为 canonical 风格
- 多行表达式使用 2 空格缩进
- 多行 application 采用“每个参数单独一行”的稳定布局
- 多行字典采用“每个键值对单独一行”的稳定布局

Readable Render 应优先提升以下场景的可检查性：

- 深层嵌套 `Do / ForEach / If / IfFound / Query`
- `Trace` 与 `Assert` 的诊断日志
- `ParseError` 的部分结构展示

Readable Render 可以与 canonical text 共享 token 顺序，但不得被要求保持单行，也不得被用于定义 AST 等价性。

---

## 5. 求值模型与效果系统

### 5.1 求值顺序

除 `Special Form` 条目另有规定外，CogLang 采用**从内到外、从左到右的 eager evaluation**。

默认规则如下：

1. 先求值最内层嵌套表达式
2. 同一 application 的参数按从左到右顺序依次求值
3. 当某个参数求值为自动传播错误值时，普通 operator 立即传播该值

#### Special Forms

以下 operator 具有冻结的特殊求值规则：

| Special Form | 求值规则 |
|-------------|----------|
| `If[cond, thenExpr, elseExpr]` | 先 eager 求值 `cond`，随后只求值一个分支 |
| `IfFound[expr, bindVar_, thenExpr, elseExpr]` | 先 eager 求值 `expr`，根据结果只求值一个分支 |
| `ForEach[collection, bindVar_, body]` | 先对 `collection` 求值一次得到快照；`body` 在每次迭代时按绑定后的 AST 求值 |
| `Do[e1, e2, ...]` | 按从左到右顺序逐个求值，不做“先求完全部参数再调用” |
| `Compose[name, params, body]` | `name` 与 `params` 先求值；`body` 作为 AST 存储，不在定义时执行 |
| `Assert[condition, message]` | 先求值 `condition`；仅在需要记录断言失败时求值 `message` |
| `Query[bindVar_, condition, options?]` | `bindVar_` 作为绑定位，不先求值；`condition` 在每个候选节点的绑定环境中求值；`options` 先求值 |

所有未列入上表的 operator，都必须遵守默认 eager 规则。

#### 绑定与作用域

- `ForEach`、`IfFound`、`Query` 的绑定变量只在对应 body / condition 的求值上下文内有效
- 绑定变量离开其作用域后不得继续引用
- `v1.1.x` baseline profile 不允许在嵌套绑定作用域中重用同名绑定变量；validator 必须拒绝这类写法，以避免捕获歧义

#### 快照语义

`ForEach` 的 `collection` 必须在迭代开始前完整求值一次。后续迭代基于该快照执行，body 中的 `Create / Update / Delete` 等副作用不得回写影响当前轮次尚未消费的集合成员。

#### 多行顺序输入的求值

若宿主接受多行顶层输入，并将其降格为 `Do[...]`，则这些行的求值顺序等同于 `Do` 的从左到右顺序，而不是额外引入新的程序块语义。

### 5.2 错误传播与恢复边界

CogLang 的错误是值，不是宿主异常。除 operator 条目另有说明外，普通 operator 在接收到错误值作为参数时，**必须直接传播该错误值**，不得继续执行其主体语义。

本规范当前冻结以下错误值集合为“自动传播错误值”：

- `NotFound[]`
- `TypeError[...]`
- `PermissionError[...]`
- `ParseError[...]`
- `StubError[...]`
- `RecursionError[...]`

`List[]` 不是错误值。它可以在某些 operator 中被判定为假，但这种真假语义不得被误写为错误传播语义。

允许构成“恢复边界”的只有两类机制：

- 语言中被显式定义为错误分支点、错误吸收点、或非致命诊断点的 operator
- profile 明确声明的宿主级恢复包装器

当前规范已明确的传播阻断点包括 `If`、`IfFound`、`Do`、`ForEach`；其具体分支或吸收语义以各 operator 条目为准。

`v1.1.0` 不引入新的通用 `Recover[...]` 核心语法。若后续版本需要，它必须与本节的自动传播规则显式对齐，而不是隐式覆盖。

除非某个条目被明确声明为 `graph-write`，普通成功返回只表示“本次执行得到某个结果”，**MUST NOT** 被解释为“该结果应自动进入图谱”。程序性中间态、局部容器和短生命周期结果默认停留在执行上下文；图谱持久化边界的权威规则见 `§6.2`。

### 5.3 效果类别

每个 operator 必须标注以下效果类别之一或组合：

- `pure`
- `graph-read`
- `graph-write`
- `meta`
- `diagnostic`
- `external`

### 5.4 确定性类别

每个 operator 必须标注以下确定性类别之一：

- `deterministic`
- `graph-state-dependent`
- `model-dependent`
- `implementation-defined`

---

## 6. 核心类型与数据模型

### 6.1 核心值类型

CogLang 的最小核心值类型如下：

| 类型 | 说明 |
|------|------|
| `String` | UTF-8 文本值；节点 ID、关系名、错误原因、标签等都可落在此类 |
| `Number` | 整数或浮点数；是否保留整数/浮点的实现级区分可由 profile 细化 |
| `Bool` | 规范布尔值；canonical surface 中对应 `True[]` / `False[]` |
| `List` | 有序序列；保留元素顺序 |
| `Dict` | 键值映射；键必须是字符串 |
| `ErrorExpr` | 以错误 Head 表示的合法 CogLang 表达式，见 §8 |

补充约束：

- 每个值都必须存在 canonical text 与 readable render
- `List` 的顺序具有语义意义；`Dict` 的键顺序不具有语义意义，但 canonical 序列化必须稳定
- `ErrorExpr` 不是宿主异常包装，而是可被表达式消费的正常值类别
- 本版不引入独立的 `Null` 或 `Maybe` 核心语法；缺失语义仍由 `NotFound[]` 等错误值或显式结构承担

### 6.2 图谱对象

CogLang 运行时可读写的图谱对象分为节点与边两类。它们首先属于原始结构层，其次才可被规范层或输出层包装。

#### 显式写图边界与禁止隐式图化

写入图谱 **MUST** 被视为显式语义动作，而不是默认副作用。

除非某个 operator 的 Normative 条目明确声明其包含 `graph-write` 语义，否则该 operator 的求值 **MUST NOT**：

- 创建新的公开图谱节点或边
- 把局部中间值自动提升为公开知识对象
- 把一次执行中的临时结果自动持久化到图谱
- 把执行期内部工件自动发布为可共享规则或公开节点

因此，以下对象在默认情况下 **MUST** 停留在执行上下文，而不是被自动图化：

- 局部绑定值
- 列表 / 字典中间结果
- 聚合、过滤、规约、排序等程序性步骤的短命产物
- trace / diagnostic / envelope 中携带的辅助字段
- adapter 或扩展实现返回的临时加工结果
- executor-internal artifact，例如内部 `Operation` 载体

若实现希望把某类结果持久化、发布或纳入图谱生命周期管理，**MUST** 通过以下方式之一显式完成：

- 调用已冻结的 `graph-write` operator
- 调用后续被明确声明为具有写图语义的 `Reserved / Experimental` operator
- 进入宿主侧已文档化、且与本规范兼容的显式发布流程

“执行成功”与“进入图谱”不是同义语。除非条目另有说明，程序性中间态的成功返回 **MUST NOT** 被解释为“应写入图谱”。

#### 节点

节点的最小稳定字段如下：

| 字段 | 要求 |
|------|------|
| `id` | 全局唯一标识 |
| `type` | 节点类型标签 |
| `confidence` | `float[0,1]` |
| `provenance` | 来源标注或其引用 |
| `created_at` | 创建时间或其等价时序标记 |
| `updated_at` | 最近更新时间或其等价时序标记 |

`v1.1.0` 当前公开基线下，公开知识图谱的主节点类型冻结为：

- `Entity`
- `Concept`
- `Rule`
- `Meta`

以下字段作为推荐扩展字段保留：

- `label`
- `embedding`
- `origin_generation`
- `trust_source`

#### 边

边的最小稳定字段如下：

| 字段 | 要求 |
|------|------|
| `source_id` | 源节点 ID |
| `target_id` | 目标节点 ID |
| `relation` | 关系类型 |
| `confidence` | `float[0,1]` |
| `provenance` | 来源标注或其引用 |

以下字段作为推荐扩展字段保留：

- `evidence`
- `origin_generation`
- `trust_source`
- `created_at`
- `updated_at`

节点与边都采用 soft-delete 语义：`confidence = 0` 的对象保留在原始结构层，但默认不参与普通查询结果。

#### `Rule` 节点与 executor 内部 `Operation` 载体

`Rule` 是公开知识图谱的一等节点类型，用于承载被验证、被追踪、或待晋升的规则对象。

`Operation` 节点在 `v1.0.2` 中曾作为动态 operator 载体出现；`v1.1.0` 保留这种 executor 内部表示的合法性，但不再把它定义为公开知识图谱主类型的一部分。若实现继续使用 `Operation` 节点承载 `Compose` 结果，它们必须满足：

- 被视为 executor-internal artifact，而不是公开知识节点类别
- 不得与 `Entity / Concept / Rule / Meta` 的公开分类混同
- 对外展示时应通过 readable render、diagnostic 或管理接口显式标注其内部身份

### 6.3 结果 Envelope

CogLang 的**语义返回值**与其**外层结果 envelope**必须区分。

- 语义返回值是 operator 按其条目直接返回的 CogLang 值
- 结果 envelope 是 transport / UI / 调试层为携带附加元数据而使用的包装对象

规范不要求每个 operator 都返回 envelope；但当 envelope 被使用时，必须遵守以下最小字段名：

| 字段 | 要求 |
|------|------|
| `value` | 语义权威返回值 |
| `metadata` | 结构化附加信息 |
| `trace_ref` | 指向相关 trace 条目或 trace 会话的引用；若无 trace 可省略 |

以下字段在 `v1.1.0` 中只保留键名，不冻结其完整 schema：

- `confidence`
- `cost`
- `gain`

也就是说：

- `value / metadata / trace_ref` 是结果 envelope 的共享核心字段
- `confidence` 是执行/推理侧常用扩展字段，而不是所有 transport / UI envelope 都必须常驻的最小字段
- `source_span / diagnostic_code` 等 UI / 诊断字段由 transport envelope 合同承接，不直接并入本条的共享核心字段
- 应用侧查询结果交换对象可以存在更丰富的结果 schema；它们不是本条定义的结果 envelope。本条只冻结表达式执行结果的最小共享字段，不冻结应用侧查询结果 schema

Envelope 约束如下：

- envelope 不得改写 `value` 的语义
- `metadata` 中的字段可以扩展，但不得覆盖最小字段名的含义
- 当 operator 本身已经返回结构化对象时，该对象仍然是语义返回值，不应被自动视为 envelope

---

## 7. Operator 规范

### 7.1 条目模板

每个 operator 条目固定写以下 **7 个核心项**：

1. **状态**：`Core / Reserved / Experimental`
2. **所属层**：`language / executor / runtime_bridge / observability / adapter`
3. **语法与签名**
4. **Validator Constraints**
5. **返回契约**
6. **语义**
7. **Baseline Availability**

并固定写以下 **4 个补充项**：

- **效果类别**
- **确定性类别**
- **可观测性要求**
- **兼容性承诺**

#### 条目书写规则

- `Core` operator 的“语义”必须是完整 Normative 描述，不能只写设计意图
- `Reserved` operator 必须至少冻结签名、验证约束、默认失败行为、trace 要求
- `Experimental` operator 可以保留实现自由度，但仍必须声明效果类别与权限边界
- 若一个 operator 依赖外部实现，其条目必须显式说明“名称已冻结”与“行为未冻结”是否同时成立
- `Validator Constraints` 只描述语法、参数个数、变量位置、名称解析、以及可静态判定的字面量约束；表达式求值后的动态类型不匹配必须写入“返回契约”或“语义”，不得混写为 validator 失败
- 对透明包装器或条件式包装器，确定性类别可以声明为“继承被包装表达式”；若其诊断事件或元数据编码仍保留实现自由度，必须在“语义”或“可观测性要求”中显式说明

#### Baseline Availability 的判定

本项描述的是**通过验证后的运行时基线可用性**，不覆盖 parser 或 validator 阶段的拒绝。

`Baseline Availability` 只允许使用以下三种形式：

- **正常执行**
- **`StubError[...]`**
- **`PermissionError[...]`**

不允许写成“由实现决定”或“可能不可用”。

若该可用性依赖 profile，条目必须写成 `Profile <name>: ...` 的形式，且 profile 名称必须在伴随文档或 manifest 中定义。

#### 后续程序层能力的准入原则

当后续版本考虑引入更强的程序层能力时，其进入 `Core` 前 **SHOULD** 至少满足以下条件：

- 该能力对图查询、图更新、规则触发、验证前表示、或可观测执行具有直接支撑作用
- 其核心语义可以在不依赖特定宿主实现技巧的前提下被稳定冻结
- 它不会把临时中间态、局部容器或一次性算法步骤默认提升为图谱对象
- 它不是主要为了对齐传统通用语言表面，或提高人类手写舒适度而引入
- 它不能更自然地被实现为 `Reserved`、`Experimental`、`extension-backed operator`、或 profile 特定能力

若某项能力主要承担：

- 列表 / 字典上的复杂规约、聚合、排序、过滤
- 强宿主耦合的本地算法、外部系统调用、或工具链桥接
- 仅服务于单次执行而不形成稳定知识对象的局部处理步骤

则它 **SHOULD** 先以 profile 扩展、注册表条目、或 `Reserved / Experimental` 条目存在，而不是直接扩大 `Core` 主干。

### 7.2 Core Operators

#### `Abstract`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Abstract[instances]
```

**Validator Constraints**：

- 必须且仅接受一个参数
- `instances` 必须是合法 CogLang 表达式

**返回契约**：

成功时返回一个结构化结果对象：

```text
{
  "cluster_id": str,
  "instance_count": int,
  "prototype_ref": str,
  "equivalence_class_ref": str,
  "selection_basis": str | Dict[...],
  "triggered": True[] | False[]
}
```

失败时：

- `instances` 求值后不是列表：`TypeError["Abstract", "instances", ...]`
- 名称与参数通过验证但当前 profile 不支持：`StubError["Abstract", ...]`

空列表输入必须返回一个非触发摘要对象；`triggered = False[]` 是合法正常结果，不是错误。

**语义**：

`Abstract` 的语义是对一组实例进行原型提取与触发判定。它：

- 接收一批待抽象的实例
- 先形成等价类或候选聚类，再形成该批实例对应的 prototype / cluster 表示
- 判断该模式是否达到“足够成熟，可以触发后续归纳”的阈值
- 返回本次抽象结果的结构化摘要

主规范只冻结 `triggered` 的字段类型与语义边界，不冻结具体阈值、具体聚类算法或具体触发启发式；这些实现起步建议应写入 companion / implementation note，而不是写入本条的规范正文。

`Abstract` 必须保留两类 provenance：

- 等价类成员列表的可追溯引用
- 代表选择或原型形成依据的可追溯说明

`Abstract` 不得因为形成代表或原型而删除、覆盖、或隐式合并原始实例；它只能为后续规范化、归纳、或解释层操作提供触发摘要。

`Abstract` **不**直接生成规则候选，**不**执行后续验证，**不**直接写入任何草稿图谱或主图谱。规则生成、验证与晋升属于 `Abstract` operator 契约之外的后续宿主或应用阶段。

**Baseline Availability**：正常执行
**效果类别**：`meta`
**确定性类别**：`model-dependent`
**可观测性要求**：

- 必须记录 `cluster_id`
- 必须记录 `instance_count`
- 必须记录 `prototype_ref`
- 必须记录 `equivalence_class_ref`
- 必须记录 `selection_basis`
- 必须记录 `triggered`

**兼容性承诺**：

- `Abstract[instances]` 这一签名在 `v1.1.x` 内冻结
- 返回值中的六个最小字段在 `v1.1.x` 内冻结
- prototype 的内部编码与具体训练后端仍可演化

#### `Equal`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Equal[a, b]
```

**Validator Constraints**：

- 必须且仅接受 2 个参数
- `a` 与 `b` 都必须是合法 CogLang 表达式
- `Equal` 不引入新的绑定变量位，也不承担名称解析扩展语义
- 动态类型差异不属于 validator 失败；它们属于运行时比较语义的一部分

**返回契约**：

- `a` 或 `b` 的求值结果为自动传播错误值时：原样传播该错误值
- 两侧值结构相等时：返回 `True[]`
- 两侧值结构不相等时：返回 `False[]`
- `Equal` 不因“值类型不同”而返回 `TypeError[...]`；异类正常值之间的比较结果就是 `False[]`

**语义**：

`Equal` 是普通 eager operator，不是 `special form`。

`Equal` 比较的是语义值的结构相等，而不是 source text、readable render 或 transport envelope 的文本相等。这里的“结构相等”沿用 `§3.2` 的全局定义：忽略 source span、render hint 与 transport-only metadata。

具体规则如下：

- 字符串按字面值比较
- 数字按数值比较
- `True[] / False[]` 按布尔值比较
- `List` 的长度必须相同，元素按位置递归比较；列表顺序具有语义意义
- `Dict` 的键集合必须相同，每个键对应值递归比较；键顺序不具有语义意义
- 结构化项 / application 的 `Head` 必须相同、参数个数必须相同、参数按位置递归比较

`Equal` 不消费自动传播错误值；若调用方需要对错误表达式做结构化匹配，应使用 `Unify` 或等价的显式检视机制。

若某个字符串恰好是节点 ID，`Equal` 也只把它当字符串值；不得隐式解引用图节点。

`Equal` 用于布尔判断和控制流，不承担差异解释职责；差异解释属于 `Compare`。

**Baseline Availability**：正常执行
**效果类别**：继承 `a` 与 `b` 的求值效果并集
**确定性类别**：继承 `a` 与 `b`；在两侧值固定后，相等判断本身必须是 `deterministic`
**可观测性要求**：

- 必须记录 `comparison_kind = equal`
- 必须记录 `result = True[] | False[]`

**兼容性承诺**：

- `Equal[a, b]` 的二参数签名在 `v1.1.x` 内冻结
- “结构相等返回 `True[]`，否则 `False[]`” 在 `v1.1.x` 内冻结
- `List` 的顺序敏感、`Dict` 的键顺序不敏感，这两条在 `v1.1.x` 内冻结
- `Equal` 不自动穿透 transport / UI 包装、不自动解引用节点字符串，这两条在 `v1.1.x` 内冻结

#### `Compare`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Compare[a, b]
```

**Validator Constraints**：

- 必须且仅接受 2 个参数
- `a` 与 `b` 都必须是合法 CogLang 表达式
- `Compare` 不引入绑定变量位，也不承担名称解析扩展语义
- 动态类型差异不属于 validator 失败；它们属于运行时差异构造语义的一部分

**返回契约**：

- `a` 或 `b` 的求值结果为自动传播错误值时：原样传播该错误值
- 两侧值结构相等时：返回空字典 `{}`
- 两侧值不相等时：返回描述结构差异的 `Dict`
- `Compare` 不因“值类型不同”而返回 `TypeError[...]`；异类正常值之间的差异仍以差异字典表达

**语义**：

`Compare` 是普通 eager operator，不是 `special form`。

`Compare` 比较的是语义值结构，而不是 source text、readable render 或 transport envelope。其输出是诊断性 delta，不是布尔值；控制流应使用 `Equal`，不是 `Compare`。

`v1.1.x` 中冻结的最小 delta 规则如下：

- 完全相等：返回 `{}`
- 原子值不相等，或结构类型/形状不同：返回 `{"expected": a, "actual": b}`
- 两侧都是同一 `Head` 且参数个数相同的 application：只为不相等的参数位置生成子差异，键名使用 `arg0`、`arg1`、`arg2` ...
- 两侧都是等长 `List`：只为不相等的位置生成子差异，键名使用 `index0`、`index1`、`index2` ...
- 两侧都是 `Dict`：只为不相等或缺失的键生成子差异；缺失一侧可用 `NotFound[]` 作为 `expected` 或 `actual`

`Compare` 不消费自动传播错误值；若调用方需要对错误表达式做结构化匹配，应使用 `Unify` 或等价的显式检视机制。

因此，`Compare[f[a, b], f[a, c]]` 的稳定结果应为：

```text
{"arg1": {"expected": "b", "actual": "c"}}
```

若某个字符串恰好是节点 ID，`Compare` 也只把它当字符串值；不得隐式解引用图节点，不得扩展成图谱级 diff。

delta 的键顺序不具有语义意义，但 canonical 序列化必须稳定。

`Compare` 的递归展开深度继承执行环境的通用递归限制；若实现对过深嵌套结构设置保护上限，则超限时必须返回 `RecursionError["Compare", ...]`，而不是爆栈、静默截断或返回部分 delta。

**Baseline Availability**：正常执行
**效果类别**：继承 `a` 与 `b` 的求值效果并集
**确定性类别**：继承 `a` 与 `b`；在两侧值固定后，delta 构造本身必须是 `deterministic`
**可观测性要求**：

- 必须记录 `comparison_kind = compare`
- 必须记录 `delta_is_empty = True[] | False[]`

**兼容性承诺**：

- `Compare[a, b]` 的二参数签名在 `v1.1.x` 内冻结
- “相等返回 `{}`，不等返回差异字典” 在 `v1.1.x` 内冻结
- 叶子差异使用 `{"expected": ..., "actual": ...}` 的最小结构在 `v1.1.x` 内冻结
- application 参数位使用 `argN` 命名、列表位置使用 `indexN` 命名的规则在 `v1.1.x` 内冻结
- `Compare` 不自动穿透 transport / UI 包装、不自动解引用节点字符串，这两条在 `v1.1.x` 内冻结

#### `Unify`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Unify[pattern, target]
```

**Validator Constraints**：

- 必须且仅接受 2 个参数
- `pattern` 与 `target` 都必须是合法 CogLang 表达式
- `pattern` 与 `target` 内允许出现 `term head` application、`atom`、命名变量、匿名通配符 `_`、字典字面量，以及 canonical value form，如 `List[...]`、`True[]`、`False[]`、`NotFound[]`、`TypeError[...]`
- `term head` 在 `Unify` 的两个参数中必须被解释为结构化项，而不是可执行 operator
- 若宿主启用了自由变量检查，则 `Unify` 必须是显式例外：两个参数中未被外层绑定上下文解析的命名变量，必须被视为本次合一调用的局部合一变量，而不是验证失败

**返回契约**：

- 可合一时：返回变量绑定字典 `{"X": value, ...}`
- 可合一但没有任何命名变量需要输出时：返回 `{}`
- 不可合一时：返回 `NotFound[]`
- `_` 只匹配，不绑定，不得出现在返回字典中
- `TypeError[...]`、`PermissionError[...]`、`NotFound[]` 等自动传播错误值在 `Unify` 中是可被匹配的正常目标项，不得因为它们是错误值就再次自动向外传播

返回字典的键名必须是命名变量去掉尾部 `_` 后的标识符核心。

**语义**：

`Unify` 的语义是对两棵 canonical value / term tree 计算最一般合一子 `MGU`。

同名命名变量在两侧和同一侧都代表同一个逻辑变量；若其约束不能同时满足，则结果为 `NotFound[]`。

`_` 匹配任意子树，但永不进入绑定结果。

`Unify[f[X_, b], f[a, Y_]]` 这类写法在 `v1.1.0` 中继续合法，其合法性依赖于小写 `f` 被明确归类为 `term head`，属于结构化项，不走默认 operator 解析。

`Unify` 是项级 / 值级结构匹配，不是图级搜索；需要在图中找满足条件的节点时，应使用 `Query` 而不是 `Unify`。

在默认 eager 语义下，参数中的普通可执行子表达式可先规约为其 canonical value；但进入合一步骤后，匹配只看结果树的结构，不再触发内部 `Head` 的再次解析或执行。

**Baseline Availability**：正常执行
**效果类别**：继承 `pattern` 与 `target` 规约阶段的效果；合一步骤本身为 `pure`
**确定性类别**：继承 `pattern` 与 `target` 的规约确定性；在给定两棵规范值树后，合一结果必须是 `deterministic`
**可观测性要求**：

- 必须记录 `unify_outcome = success | not_found`
- 必须记录绑定结果大小

**兼容性承诺**：

- `Unify[pattern, target]` 的二参数签名在 `v1.1.x` 内冻结
- 成功返回绑定字典、失败返回 `NotFound[]` 的二分返回形态在 `v1.1.x` 内冻结
- 返回字典的键名去尾部 `_` 的规则在 `v1.1.x` 内冻结
- `term head` 在 `Unify` 中作为结构化项参与匹配、而不参与默认 operator 解析，这一点在 `v1.1.x` 内冻结
- 自动传播错误值可被 `Unify` 结构化匹配、而不是再次自动传播，这一点在 `v1.1.x` 内冻结

#### `Match`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Match[pattern, target]
```

**Validator Constraints**：

- 与 `Unify` 完全相同
- `Match` 不引入独立的 pattern grammar；它直接继承 `Unify` 对 `term head`、命名变量、`_`、canonical value form 的解释规则

**返回契约**：

- 与 `Unify` 完全相同
- 可合一时返回绑定字典；不可合一时返回 `NotFound[]`；`_` 不进入返回结果

**语义**：

`Match` 是 `Unify` 的精确别名，语义、返回形态、错误匹配能力、以及 `operator head / term head` 的解释规则都必须与 `Unify` 保持完全一致。

保留 `Match` 的原因是它更接近用户直觉；保留 `Unify` 的原因是它与逻辑 / 形式方法术语一致。

`Match / Unify` 做的是项级匹配，不是图级 pattern search；图级命中检索仍属于 `Query`。

**Baseline Availability**：正常执行
**效果类别**：与 `Unify` 完全相同
**确定性类别**：与 `Unify` 完全相同
**可观测性要求**：

- 与 `Unify` 完全相同
- trace 中可额外记录 `alias_of = "Unify"`

**兼容性承诺**：

- `Match[pattern, target]` 在 `v1.1.x` 内必须保持为 `Unify[pattern, target]` 的精确别名
- 不允许在 `v1.1.x` 内把 `Match` 演化成更宽的图模式查询、正则匹配、或近似匹配接口
- `Match` 与 `Unify` 的返回形态、键名规则、以及错误匹配行为不得漂移

#### `Get`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Get[source, key]
```

**Validator Constraints**：

- 必须且仅接受 2 个参数
- `source` 与 `key` 都必须是合法 CogLang 表达式
- `Get` 的分派属于运行时语义，不把 `source` 或 `key` 的动态类型约束写成 validator 失败

**返回契约**：

- `source` 或 `key` 的求值结果为自动传播错误值时：原样传播该错误值
- `source` 求值为 `Dict` 且 `key` 求值为字符串时：返回对应键值；键不存在时返回 `NotFound[]`
- `source` 求值为 `List[...]` 且 `key` 求值为整数时：按 `0-based` 索引返回元素；索引越界时返回 `NotFound[]`
- `source` 求值为字符串节点 ID 且 `key` 求值为字符串时：返回该节点的对应属性值；节点不存在、节点不可见、或属性不存在时返回 `NotFound[]`
- `source` 求值为其他正常值时：`TypeError["Get", "source", ...]`
- 分派已确定但 `key` 类型与该分派不匹配时：`TypeError["Get", "key", ...]`

**语义**：

`Get` 是普通 eager operator，不是 `special form`。

`Get` 的运行时分派顺序冻结为：

1. `Dict`
2. `List`
3. 字符串节点 ID

`Get` 统一承载“字典取键 / 列表取索引 / 节点属性读取”这三类常用访问，不拆分为多个核心 operator。

`Get` 的规范输入对象是 canonical CogLang 值。`transport envelope`、`readable render`、宿主诊断对象等外层包装不得被 `Get` 规范性穿透读取；宿主若有包装，必须先解包再进入 CogLang 求值。

**Baseline Availability**：正常执行
**效果类别**：`graph-read`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录 `dispatch_branch = dict | list | node_attr`
- 必须记录 `result_kind = hit | not_found | type_error`

**兼容性承诺**：

- `Get[source, key]` 的二参数签名在 `v1.1.x` 内冻结
- 三路分派模型在 `v1.1.x` 内冻结
- “键不存在 / 索引越界 / 属性不存在 / 节点不存在或不可见返回 `NotFound[]`” 在 `v1.1.x` 内冻结
- 列表索引的 `0-based` 规则在 `v1.1.x` 内冻结

#### `Query`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Query[bindVar_, condition]
Query[bindVar_, condition, options]
```

其中二参数形式等价于：

```text
Query[bindVar_, condition, {"k": 1, "mode": "default"}]
```

**Validator Constraints**：

- 只允许 2 个或 3 个参数
- `bindVar_` 必须是变量
- `condition` 必须是合法 CogLang 表达式
- 若提供第三个参数，其位置必须是合法 CogLang 表达式
- 名称未解析、变量位置非法等问题属于验证失败，不进入执行阶段

**返回契约**：

- 成功命中：`List[node_id, ...]`
- 无命中：`List[]`
- 第三个参数求值后若不是字典：`TypeError["Query", "options", ...]`
- `options["k"]` 求值后若不是非负整数或字符串 `"inf"`：`TypeError["Query", "k", ...]`
- `options["mode"]` 求值后若不是字符串：`TypeError["Query", "mode", ...]`
- 条件求值失败：传播底层错误值

返回的节点列表必须采用稳定顺序；除非条目另有说明，默认使用节点 ID 的 canonical 升序。

**语义**：

`Query` 在所有可见节点中搜索满足 `condition` 的节点。其核心语义继承 `v1.0.2` 的“绑定变量 + 条件表达式”模型，但 `v1.1.0` 为查询接口增加了独立的 `k` 与 `mode` 字段。

- `k` 表示 `condition` 求值时允许使用的图扩展深度上界，默认 `1`
- `mode` 表示执行策略，默认 `"default"`
- `k` 与 `mode` 是两个独立维度，不得被实现耦合成单一隐式参数

`k` 的最小语义约束如下：

- `k = 0`：只允许节点局部属性判断，不允许图邻接扩展
- `k = 1`：允许直接邻居级访问
- `k = N`：允许最多 `N` 跳的图扩展
- `k = "inf"`：取消固定跳数上界，但仍受 profile 预算与权限约束

如果 `condition` 只引用节点局部属性，则不同 `k` 不得改变其结果集。

在 `Core` 语义中，`mode = "default"` 是唯一要求实现的默认模式。无论当前实现声明 `Baseline` 还是 `Enhanced`，当调用者省略第三参数，或显式给出 `{"mode": "default"}` 时，都必须落到该默认模式。非默认模式属于保留扩展点，可由 profile 或运行时注册表补充。

空结果 `List[]` 表示“执行成功但没有命中”，不得与执行错误混同。

`Query` 的结果是 canonical 内部表示的一部分；任何面向 `delta+` 默认路径的人类可读渲染，都是其外层接口契约，而不是 `Query` 核心语法的一部分。

**Baseline Availability**：正常执行
**效果类别**：`graph-read`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录 `condition` 的 canonical 形式
- 必须记录 `k`
- 必须记录 `mode`
- 必须记录结果计数与耗时

**兼容性承诺**：

- 二参数形式在 `v1.1.x` 内保持有效
- `options` 中 `k` / `mode` 这两个键在 `v1.1.x` 内冻结
- 非默认 `mode` 的具体集合不在本条目冻结

#### `AllNodes`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
AllNodes[]
```

**Validator Constraints**：

- 不接受任何参数

**返回契约**：

- 成功：`List[node_id, ...]`
- 空图：`List[]`

返回顺序必须稳定；除非条目另有说明，默认使用节点 ID 的 canonical 升序。

**语义**：

`AllNodes` 返回所有可见节点的 ID 列表。这里的“可见”指：

- 节点 `confidence > 0`
- 节点未被当前 profile 隐藏

`AllNodes` 是查询族的基础构件，不承担额外的筛选、排序策略选择或执行模式切换。

**Baseline Availability**：正常执行
**效果类别**：`graph-read`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录结果计数与耗时

**兼容性承诺**：

- `AllNodes[]` 的无参数签名在 `v1.1.x` 内冻结

#### `Traverse`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Traverse[node, relation]
```

**Validator Constraints**：

- 必须且仅接受 2 个参数
- `node` 与 `relation` 必须是合法 CogLang 表达式

**返回契约**：

- 成功命中：`List[node_id, ...]`
- 无命中、起点不存在、或起点不可见：`List[]`
- `node` 求值后不是字符串：`TypeError["Traverse", "node", ...]`
- `relation` 求值后不是字符串：`TypeError["Traverse", "relation", ...]`
- 底层参数求值若得到自动传播错误值：原样传播该错误值

返回的节点列表必须采用稳定顺序；除非条目另有说明，默认使用目标节点 ID 的 canonical 升序。

**语义**：

`Traverse` 从起点节点出发，沿所有关系类型等于 `relation` 的**可见出边**进行一步遍历，返回所有可见目标节点的 ID 列表。

“可见”至少要求：

- 边 `confidence > 0`
- 目标节点 `confidence > 0`
- 边与目标节点未被当前 profile 隐藏

`Traverse` 不负责反向遍历。若要表达“哪些节点通过某关系指向当前节点”，应使用 `Query` 或等价图搜索在外层表达。

`Traverse` 将“起点不存在”视为“没有可见邻居”，而不是权限错误或解析错误。

**Baseline Availability**：正常执行
**效果类别**：`graph-read`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录起点节点 ID 或其摘要
- 必须记录 `relation`
- 必须记录结果计数与耗时

**兼容性承诺**：

- `Traverse[node, relation]` 的二参数签名在 `v1.1.x` 内冻结
- “起点不存在返回 `List[]`” 在 `v1.1.x` 内冻结
- “仅遍历可见出边，不含反向遍历” 在 `v1.1.x` 内冻结

#### `ForEach`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
ForEach[collection, bindVar_, body]
```

**Validator Constraints**：

- 必须且仅接受 3 个参数
- `collection` 与 `body` 必须是合法 CogLang 表达式
- `bindVar_` 必须是合法变量位
- `bindVar_` 只在 `body` 的求值作用域内有效；越界引用属于验证失败
- 在嵌套绑定作用域中重用同名 `bindVar_` 属于验证失败

**返回契约**：

- `collection` 求值为 `List[v1, ..., vn]` 时：返回 `List[r1, ..., rn]`
- `collection` 求值为自动传播错误值时：返回 `List[]`
- `collection` 求值为非列表的正常值时：`TypeError["ForEach", "collection", ...]`

每个 `ri` 是将第 `i` 个元素绑定到 `bindVar_` 后求值 `body` 的结果；若某次迭代产生错误值，该错误值保留在对应结果位置，不导致整轮迭代提前终止。

**语义**：

`ForEach` 是冻结的 `special form`。它先对 `collection` 求值一次得到快照，再按快照顺序逐个求值 `body`。

核心约束如下：

- `collection` 只在迭代开始前求值一次
- `body` 在每次迭代时使用当前元素的绑定环境求值
- `bindVar_` 的作用域严格限定在 `body` 内
- body 中的副作用不得回写改变当前轮次尚未消费的快照成员

若执行环境在某轮 `body` 中使显式写图动作生效，则后续迭代里的图查询可以观察到这些已生效变更；但这种可见性不得回溯改变本轮开始前已经冻结的 `collection` 快照成员与迭代顺序。

`ForEach` 是显式传播阻断点：当 `collection` 本身为错误值时，它返回 `List[]` 而不是继续自动传播该错误值。

**Baseline Availability**：正常执行
**效果类别**：继承 `collection` 与 `body` 的效果并集
**确定性类别**：继承 `collection` 与 `body`；迭代顺序本身必须稳定
**可观测性要求**：

- 必须记录快照大小
- 必须记录迭代顺序
- 必须记录结果计数与耗时

**兼容性承诺**：

- `ForEach[collection, bindVar_, body]` 的三参数签名在 `v1.1.x` 内冻结
- 快照语义在 `v1.1.x` 内冻结
- `collection` 为错误值时返回 `List[]` 的行为在 `v1.1.x` 内冻结

#### `Do`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Do[expr1, expr2, expr3, ...]
```

**Validator Constraints**：

- 必须至少接受 1 个参数
- 每个参数都必须是合法 CogLang 表达式
- `Do` 本身不引入新的绑定变量位；绑定与作用域由内部 operator 自身处理

**返回契约**：

- 成功时返回最后一个子表达式的求值结果
- 前序子表达式的返回值被丢弃，但其副作用保留
- 某一步返回自动传播错误值时，`Do` 不自动中止；后续步骤继续执行
- 若最后一个子表达式返回错误值，则 `Do` 返回该错误值
- `Do` 不返回“所有步骤结果的聚合列表”；除非最后一个子表达式自身返回 `List[...]` 或其他聚合值

**语义**：

`Do` 是冻结的 `special form`。它按从左到右顺序逐个求值子表达式，不做“先求完所有参数再调用”的 eager 展开。

`Do` 表达的是顺序执行容器，而不是依赖链恢复器。若要根据前一步结果决定后续控制流，必须显式使用 `If`、`IfFound`、`ForEach` 等结构，而不是依赖 `Do` 的隐式短路。

若宿主接受多行顶层输入，并将其降格为 `Do[...]`，其规范语义等同于本条目的从左到右顺序执行，而不是引入额外块语义。

**Baseline Availability**：正常执行
**效果类别**：继承其子表达式效果并集
**确定性类别**：继承其子表达式序列；求值顺序本身必须确定为从左到右
**可观测性要求**：

- 必须记录步骤数
- 必须记录步骤顺序
- 必须记录最终返回值摘要

**兼容性承诺**：

- `Do[e1, e2, ...]` 的从左到右顺序求值在 `v1.1.x` 内冻结
- “`Do` 返回最后一个已求值子表达式的结果，而不是全部中间结果” 在 `v1.1.x` 内冻结
- “前序步骤出错不自动中止后续步骤” 在 `v1.1.x` 内冻结
- “多行顶层输入可降格为 `Do[...]`，但不构成额外块语义” 在 `v1.1.x` 内冻结

#### `If`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
If[condition, thenExpr, elseExpr]
```

**Validator Constraints**：

- 必须且仅接受 3 个参数
- `condition`、`thenExpr`、`elseExpr` 都必须是合法 CogLang 表达式
- `If` 本身不引入新的绑定变量位；绑定与作用域仅由其内部子表达式中的其他 operator 自身处理

**返回契约**：

- 先求值 `condition`
- 若 `condition` 的结果为真值：返回 `thenExpr` 的求值结果
- 若 `condition` 的结果为假值：返回 `elseExpr` 的求值结果
- `condition` 的结果若属于自动传播错误值集合：不继续自动向外传播，而是按假值处理并进入 `elseExpr`
- 被执行分支若返回错误值：原样返回该错误值
- 未被执行的分支不得求值，其潜在副作用与错误不得发生

**语义**：

`If` 是冻结的 `special form`。它先 eager 求值 `condition`，随后只求值一个分支。

`v1.1.x` 中冻结的假值集合为：

- `False[]`
- `NotFound[]`
- `List[]`
- `0`
- `0.0`
- `""`
- `§8` 定义的自动传播错误值

除上述假值外，其他所有合法 CogLang 值都判定为真。

`If` 区分的是“真/假”，不是“有结果/无结果”。因此 `List[]` 在 `If` 中是假，但它不是错误值；这一点必须与 `IfFound` 的语义保持分层。

`If` 是显式传播阻断点，但不是通用错误恢复器；需要按“缺失/出错”分流时，应使用 `IfFound` 而不是复用 `If`。

**Baseline Availability**：正常执行
**效果类别**：继承 `condition` 与被执行分支的效果并集
**确定性类别**：继承 `condition` 与被执行分支；分支选择本身必须确定
**可观测性要求**：

- 必须记录 `condition_result_kind`
- 必须记录 `branch_taken = then | else`

**兼容性承诺**：

- `If[condition, thenExpr, elseExpr]` 的三参数签名在 `v1.1.x` 内冻结
- “仅执行一个分支”的 `special form` 语义在 `v1.1.x` 内冻结
- 本条目定义的假值判定表在 `v1.1.x` 内冻结
- “自动传播错误值在 `If` 中按假值处理” 在 `v1.1.x` 内冻结

#### `IfFound`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
IfFound[expr, bindVar_, thenExpr, elseExpr]
```

**Validator Constraints**：

- 必须且仅接受 4 个参数
- `expr`、`thenExpr`、`elseExpr` 必须是合法 CogLang 表达式
- `bindVar_` 必须是合法变量位，且仅在 `thenExpr` 的求值作用域内有效
- `bindVar_` 在 `elseExpr` 或外层作用域中的越界引用属于验证失败
- 在嵌套绑定作用域中重用同名 `bindVar_` 属于验证失败

**返回契约**：

- 若 `expr` 求值结果既不是 `NotFound[]` 也不是自动传播错误值，则将结果绑定到 `bindVar_`，返回 `thenExpr` 的求值结果
- 若 `expr` 求值结果为 `NotFound[]` 或自动传播错误值，则返回 `elseExpr` 的求值结果
- `List[]` 不是错误值；`expr -> List[]` 时，必须进入 `thenExpr` 分支
- `thenExpr` 或 `elseExpr` 自身求值失败时，传播对应底层错误值

**语义**：

`IfFound` 是冻结的 `special form`。它先 eager 求值 `expr`，然后只求值一个分支。

`IfFound` 区分的是“结果可用”与“缺失/出错”，不是“真/假”。因此：

- `NotFound[]` 进入 `elseExpr`
- 自动传播错误值进入 `elseExpr`
- `List[]` 进入 `thenExpr`

`IfFound` 是显式恢复边界：它不让 `expr` 的缺失值或错误值继续自动向外传播，而是把控制权交给 `elseExpr`。

`IfFound` 也是当前 `v1.1.0` 中正式冻结的 bind-and-continue 惯用法：当 `expr` 产出的是后续步骤需要消费的值时，调用者可以使用 `IfFound[expr, v_, thenExpr, elseExpr]` 将该值显式绑定进 `thenExpr`，而不改变 `Do` “只负责顺序执行、不负责步间绑定”的语义。该惯用法不把 `IfFound` 重新定义为通用顺序构件，但它是当前发布版表达“先产值、后消费”链条的官方写法。

**Baseline Availability**：正常执行
**效果类别**：继承 `expr` 与被执行分支的效果并集
**确定性类别**：继承 `expr` 与被执行分支
**可观测性要求**：

- 必须记录 `branch_taken = then | else`
- 必须记录 `source_expr_result_kind = normal | not_found | error`

**兼容性承诺**：

- `IfFound[expr, bindVar_, thenExpr, elseExpr]` 的四参数签名在 `v1.1.x` 内冻结
- `List[]` 进入 `thenExpr` 分支的行为在 `v1.1.x` 内冻结
- 自动传播错误值集合由 `§8` 统一定义；本条目只消费该集合，不单独扩展

#### `Compose`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Compose[name, params, body]
```

**Validator Constraints**：

- 必须且仅接受 3 个参数
- `name` 必须是与 `operator head` 兼容的字符串字面量
- `params` 必须是字面量形态的 `List[var1_, var2_, ...]`
- `params` 内的变量名必须互不重复，且不得使用匿名 `_`
- `body` 必须是合法 CogLang 表达式
- `body` 的验证上下文必须显式加入 `params` 中声明的变量，以及当前被注册的 operator 名称自身，以支持递归定义

**返回契约**：

- 成功：返回最小 registration receipt，对外至少包含：

```text
{
  "operator_name": <string>,
  "scope": "graph-local"
}
```

- `name` 不是与 `operator head` 兼容的字符串字面量：验证失败
- `params` 不是由互不重复命名变量组成的字面量列表：验证失败
- 若 `name` 与静态内置 operator 或同一图动态作用域中的既有定义冲突：`TypeError["Compose", "name", "operator already exists or reserved", ...]`
- 当前 profile 不允许图动态定义：`PermissionError["Compose", "capability denied", ...]`

实现可以在 transport / diagnostics / 管理 API 中附带内部 definition handle，但该 handle 不是公开语义返回值的一部分。

**语义**：

`Compose` 是冻结的 `special form`。它读取字面量 `name` 与 `params`，但**不**在定义时执行 `body`；`body` 以 AST 形式存储为图动态 operator 定义。

成功后，该定义进入 `§10` 的“图内动态 operator 定义”层。`Compose` 只负责注册图内动态定义；名称解析顺序、注册表扩展、外部 adapter 与 capability 约束由 `§10` 统一规定。

`Compose` 不等同于通用插件注册接口，也不负责冻结运行时注册表或外部 adapter 的行为。

`Compose` 的规范语义是“注册图动态 operator 定义”，而不是“创建公开知识节点”。实现可以使用 executor-internal `Operation` 载体承载该定义，但这类载体不应被误当成公开知识图谱主类型。

定义出的 operator 可以递归调用自身。默认 baseline profile 必须至少支持递归深度 100；超限时返回 `RecursionError[...]`。

**Baseline Availability**：正常执行
**效果类别**：`meta`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录 `registered_name`
- 必须记录 `param_count`
- 必须记录目标作用域为 `graph-local`
- 必须记录 `registration_outcome`

**兼容性承诺**：

- `Compose[name, params, body]` 的三参数签名在 `v1.1.x` 内冻结
- `name` 为字符串字面量、`params` 为命名变量字面量列表的约束在 `v1.1.x` 内冻结
- “`body` 在定义时不执行” 在 `v1.1.x` 内冻结
- “静态内置定义不可被 `Compose` 覆盖” 在 `v1.1.x` 内冻结
- “默认 baseline profile 的递归深度下限为 100” 在 `v1.1.x` 内冻结

#### `Create`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Create[nodeType, attrs]
Create["Edge", attrs]
```

**Validator Constraints**：

- 必须且仅接受 2 个参数
- `nodeType` 与 `attrs` 都必须是合法 CogLang 表达式
- `Create["Edge", attrs]` 表示边创建模式；其余情况进入节点创建模式
- 基于求值结果的类型约束、字段约束与权限约束不属于 validator 阶段

**返回契约**：

- `nodeType` 求值后不是字符串：`TypeError["Create", "type", ...]`
- `attrs` 求值后不是字典：`TypeError["Create", "attrs", ...]`
- 节点模式下，`nodeType` 不是 `Entity / Concept / Rule / Meta`：`TypeError["Create", "type", "Entity|Concept|Rule|Meta|Edge", ...]`
- 节点模式下，`attrs` 显式提供保留键 `type`：`TypeError["Create", "attrs", "reserved key type", ...]`
- 节点模式下，`attrs` 显式提供的 `id` 已存在：`TypeError["Create", "id", "node id already exists", ...]`
- 节点或边模式下，若显式提供 `confidence` 但不是 `(0, 1]` 内数值：`TypeError["Create", "confidence", ...]`
- 边模式下，`attrs` 缺少 `from`、`to`、`relation_type` 任一必填字段：`TypeError["Create", "Edge", "missing required field", ...]`
- 边模式下，`from`、`to`、`relation_type` 任一字段求值后不是字符串：`TypeError["Create", "Edge", "invalid field type", ...]`
- 边模式下，`from` 或 `to` 指向的节点不存在或不可见：`NotFound[]`
- 当前 profile 禁止图写入：`PermissionError["Create", "graph_write"]`
- 节点模式成功：返回节点最终采用的 ID 字符串；若 `attrs.id` 缺失，则这是执行环境为该次创建分配的唯一 ID
- 边模式成功：返回 `List[from, relation_type, to]`

**语义**：

`Create` 在节点模式下创建公开知识图谱节点，在边模式下创建公开边对象。

节点模式的第一参数 `nodeType` 是公开主类型的唯一权威来源；`attrs` 只负责补充业务属性与可选 `id / confidence`。因此：

- 公开节点 `type` 只允许 `Entity / Concept / Rule / Meta`
- 旧式 `attrs["type"] = "Person"` 之类业务分类写法在 `v1.1.x` 中不再合法
- 业务分类应通过非保留业务字段或图结构表达，但本版不冻结统一字段名

`Create["Rule", attrs]` 创建的是公开 `Rule` 节点，而不是可执行 operator 定义；图内动态 operator 仍由 `Compose` 负责。

边模式中的调用面键名 `from / to / relation_type` 是 call-surface alias；实现内部若采用 `source_id / target_id / relation`，必须做无歧义映射，但不得把这种内部命名差异暴露成语义差异。

节点模式下，若 `attrs.id` 显式给出且未冲突，则执行环境必须使用该值作为本次创建采用的节点 ID；若 `attrs.id` 缺失，则执行环境必须在形成内部写入请求、`WriteBundleCandidate` 或等价宿主提交对象之前分配唯一 ID，并以该 ID 作为语言层返回值与后续内部引用的共同标识。ID 的具体格式与生成策略由执行环境定义；一种常见做法是预分配 UUID。

若内部实现采用 `source_id / target_id / relation`，则 `from / to / relation_type` 到内部字段的映射必须在构造内部写入请求、bundle 校验输入或等价宿主提交对象时完成；不得把这一步推迟到提交后，从而让内部引用校验面对未映射的 call-surface 字段。

`Create` 失败时不得产生部分写入。

本条冻结的是语言级写意图与成功/失败语义，不规定宿主的持久化提交路径。若上层架构采用 `WriteBundle`、owning-module 或其他代理提交流程，执行器可以先形成中间写入候选，再由宿主在提交成功后映射回本条的语言级返回契约。相同分层适用于 `Update / Delete`。

**Baseline Availability**：正常执行
**效果类别**：`graph-write`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录 `create_mode = node | edge`
- 必须记录目标主类型或 `relation_type`
- 必须记录 `creation_outcome`

**兼容性承诺**：

- `Create[nodeType, attrs]` 与 `Create["Edge", attrs]` 这两种调用外形在 `v1.1.x` 内冻结
- 节点成功返回字符串 ID、边成功返回三元组的行为在 `v1.1.x` 内冻结
- `Create["Edge", ...]` 中的 `"Edge"` 是调用模式标记，而不是公开主节点类型
- 公开节点 `type` 由第一参数决定，`attrs` 不得覆写该字段，这一点在 `v1.1.x` 内冻结

#### `Update`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Update[target, changes]
```

**Validator Constraints**：

- 必须且仅接受 2 个参数
- `target` 与 `changes` 都必须是合法 CogLang 表达式
- `Update` 在 `v1.1.x` 主规范中只覆盖节点更新，不包含边更新模式

**返回契约**：

- `target` 求值后不是字符串：`TypeError["Update", "target", ...]`
- `changes` 求值后不是字典：`TypeError["Update", "changes", ...]`
- 目标不存在：`NotFound[]`
- 目标已软删除：`PermissionError["Update", ...]`
- 当前 profile 禁止写入，或目标属于不可修改对象：`PermissionError["Update", ...]`
- `changes` 试图改写受保护系统字段，如 `id / type / provenance / created_at / updated_at`：`TypeError["Update", "changes", "writable field set", ...]`
- `changes["confidence"] = 0`：`TypeError["Update", "changes", "use Delete for soft-delete", ...]`
- `changes["confidence"]` 若存在但不是 `(0, 1]` 内数值：`TypeError["Update", "confidence", ...]`
- 成功：`True[]`

**语义**：

`Update` 是单节点、部分字段覆盖式更新；未出现在 `changes` 中的字段必须保持不变。

`Update` 不得承担 soft-delete 或 restore 语义；软删除只能走 `Delete`，恢复不属于当前 `Core` 条目。

运行时管理字段如 `updated_at` 由实现刷新；普通 `Update` 不得伪造覆盖系统管理字段。

`Update["some_rule", ...]` 修改的是公开 `Rule` 节点内容，不得隐式改写 `Compose` 注册的图内动态 operator 定义。

`Update` 失败时不得部分应用变更。

**Baseline Availability**：正常执行
**效果类别**：`graph-write`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录目标节点 ID
- 必须记录变更字段集合
- 必须记录 `update_outcome`

**兼容性承诺**：

- `Update[target, changes]` 的二参数签名在 `v1.1.x` 内冻结
- “目标不存在返回 `NotFound[]`” 与 “目标已软删除返回 `PermissionError[...]`” 在 `v1.1.x` 内冻结
- `Update` 不提供边更新模式这一边界在 `v1.1.x` 内冻结
- `Update` 不允许把 `confidence` 写成 `0` 以模拟删除，这一点在 `v1.1.x` 内冻结

#### `Delete`

**状态**：`Core`
**所属层**：`language`
**语法与签名**：

```text
Delete[target]
Delete["Edge", attrs]
```

**Validator Constraints**：

- 只允许 1 参数或 2 参数两种形式
- `Delete[target]` 表示节点删除模式
- `Delete["Edge", attrs]` 表示边删除模式；两参数形式下第一参数必须是字面字符串 `"Edge"`
- 所有参数位置都必须是合法 CogLang 表达式

**返回契约**：

- 节点模式下，`target` 求值后不是字符串：`TypeError["Delete", "target", ...]`
- 边模式下，`attrs` 求值后不是字典：`TypeError["Delete", "attrs", ...]`
- 边模式下，缺少 `from`、`to`、`relation_type` 或字段值不是字符串：`TypeError["Delete", "Edge", ...]`
- 节点模式成功：返回被软删除的节点 ID 字符串
- 边模式成功：返回被软删除边的三元组 `List[from, relation_type, to]`
- 节点或边不存在：`NotFound[]`
- 节点或边已软删除：`NotFound[]`
- 当前 profile 禁止删除，或目标属于受保护对象：`PermissionError["Delete", ...]`

**语义**：

`Delete` 只做 soft-delete，不做物理清除；其规范效果是把目标对象的 `confidence` 置为 `0`，并保留历史。

节点与边在被软删除后，默认不再参与 `AllNodes`、`Traverse`、`Query` 等普通可见性路径。

`Delete` 必须是幂等的；对已删除对象再次删除，返回 `NotFound[]`。

`Delete["Edge", attrs]` 删除的是公开边对象，不要求暴露内部 edge handle。其调用面键名 `from / to / relation_type` 仍是 call-surface alias，而不是内部存储 schema 的唯一命名。

`Delete["some_rule"]` 删除的是公开 `Rule` 节点；它不自动等价于注销某个 `Compose` 定义，也不自动清理所有引用该规则的证据边。

**Baseline Availability**：正常执行
**效果类别**：`graph-write`
**确定性类别**：`graph-state-dependent`
**可观测性要求**：

- 必须记录 `delete_mode = node | edge`
- 必须记录目标对象引用
- 必须记录 `delete_outcome`

**兼容性承诺**：

- 节点一参数形式与边二参数形式在 `v1.1.x` 内冻结
- soft-delete 而非 hard-delete 的语义在 `v1.1.x` 内冻结
- “已不存在或已删除返回 `NotFound[]`” 的幂等语义在 `v1.1.x` 内冻结

#### `Trace`

**状态**：`Core`
**所属层**：`observability`
**语法与签名**：

```text
Trace[expr]
```

**Validator Constraints**：

- `expr` 必须是合法 CogLang 表达式

**返回契约**：

- 返回值必须与直接执行 `expr` 的结果完全一致
- `expr` 返回错误值时，`Trace` 必须原样返回该错误值

trace sink 不可用不得覆盖业务返回值。

**语义**：

`Trace` 是透明包装器。它执行 `expr`，并将本次执行写入可观测性系统，但不改变 `expr` 的语义、返回值或错误传播行为。

`Trace` 只负责表达式级执行记录，不负责任务级 ROI、规则级回滚、或成本级汇总事件。

**Baseline Availability**：正常执行
**效果类别**：`diagnostic`
**确定性类别**：继承 `expr`；trace 事件编码为 `implementation-defined`
**可观测性要求**：

- 必须至少记录 `expr_id`
- 必须至少记录 `parent_id`
- 必须至少记录 `canonical_expr`
- 必须至少记录 `result_summary`
- 必须至少记录 `duration_ms`
- 必须至少记录 `effect_class`

**兼容性承诺**：

- `Trace[expr]` 的透明包装语义在 `v1.1.x` 内冻结

#### `Assert`

**状态**：`Core`
**所属层**：`observability`
**语法与签名**：

```text
Assert[condition, message]
```

**Validator Constraints**：

- `condition` 必须是合法 CogLang 表达式
- `message` 必须是合法 CogLang 表达式

**返回契约**：

- 返回 `condition` 的求值结果
- 若 `condition` 自身求值出错，原样传播该错误
- 断言失败本身不是 CogLang 运行时错误

**语义**：

`Assert` 执行非致命断言。它先求值 `condition`；若结果为假，则产出断言失败事件，但不终止当前推理链。

`message` 仅在需要记录断言失败时求值。

`Assert` 适用于在组合操作、规则触发、或调试路径中暴露异常状态，而不是替代错误传播机制。

**Baseline Availability**：正常执行
**效果类别**：`diagnostic`
**确定性类别**：继承 `condition`；断言事件编码为 `implementation-defined`
**可观测性要求**：

- 断言失败时必须记录结构化 assertion / anomaly 事件
- 事件必须能被上层纳入错误分类与回滚审计

**兼容性承诺**：

- `Assert` 的非致命语义在 `v1.1.x` 内冻结

#### Core 条目范围说明

本节只冻结本轮优先收口的 `Core` operator 条目。其余仍保留在 catalog 中的旧条目，后续将分别判断是迁入 `Core`、转入 `Reserved`，还是继续维持 `Carry-forward`；不再默认假设它们都会进入本模板。

### 7.3 Reserved Operators

#### `Explain`

**状态**：`Reserved`
**所属层**：`observability`
**语法与签名**：

```text
Explain[expr]
```

**Validator Constraints**：

- `expr` 必须是合法 CogLang 表达式

**返回契约**：

- 在支持该能力的 profile 中，返回执行计划描述对象
- 在默认基线 profile 中，允许返回 `StubError["Explain", ...]`

**语义**：

`Explain` 的语义是“非执行式计划预览”。它用于在不真正执行 `expr` 的前提下，返回对执行步骤、代价或计划结构的说明。

`Explain` 一旦实现：

- 不得产生 graph write
- 不得产生外部副作用
- 不得替代 `Trace`

**Baseline Availability**：`StubError[...]`
**效果类别**：`meta`
**确定性类别**：`implementation-defined`
**可观测性要求**：

- 调用 `Explain` 必须至少留下 `meta` 或 `stub` 事件

**兼容性承诺**：

- `Explain[expr]` 的签名在 `v1.1.x` 内冻结
- 返回对象的完整 schema 暂未冻结

#### `Inspect`

**状态**：`Reserved`
**所属层**：`meta`
**语法与签名**：

```text
Inspect[target]
```

**Validator Constraints**：

- `target` 必须是合法 CogLang 表达式

**返回契约**：

- 在支持该能力的 profile 中，返回对象结构描述数据
- 在默认基线 profile 中，允许返回 `StubError["Inspect", ...]`

**语义**：

`Inspect` 的语义是“把对象结构作为数据返回”，用于检视值、结构化项、或实现公开暴露的对象描述。它不执行计划预览，也不提供时序 trace。

`Inspect` 一旦实现：

- 不得替代 `Trace`
- 不得替代 `Explain`
- 不得因为检视成功就自动暴露宿主私有内部结构

**Baseline Availability**：`Profile Baseline: StubError["Inspect", ...]`; `Profile Enhanced: 正常执行`
**效果类别**：`meta`
**确定性类别**：`implementation-defined`
**可观测性要求**：

- 调用 `Inspect` 必须至少留下 `meta` 或 `stub` 事件

**兼容性承诺**：

- `Inspect[target]` 的一参数签名在 `v1.1.x` 内冻结
- 默认基线 profile 的 `StubError[...]` 留桩路径在 `v1.1.x` 内冻结
- 返回对象的完整 schema 暂未冻结

#### Reserved 范围说明

以下能力在本轮只作为保留位，不在本节写成 `Core`：

- 显式限定名称的具体表面语法
- 非默认 `Query.mode`
- 查询成本 / 信息增益估计
- 规则候选 envelope
- 规则发布与回滚链的完整 schema

### 7.4 Experimental Operators

本节记录**已进入讨论但尚未具备稳定语义承诺**的 operator 方向。

进入 `Experimental` 的条目至少必须满足：

- 名称、层级、效果类别、权限边界有初步描述
- 尚未满足 `Reserved` 所要求的“签名 + 默认失败行为 + trace 要求”冻结强度
- 实现者不得把它们作为稳定依赖对外承诺

当前典型实验方向包括：

- 通用 `Recover[...]`
- 更强的 `InspectSelf[...]`
- 规则自修改相关 operator
- adapter 专用高耦合 operator

这些条目可以出现在附录、设计记录、或实验 profile 中，但在进入 `Reserved` 之前，不应写入 `Core` operator 目录。

---

## 8. 错误与诊断契约

### 8.1 错误表达式

CogLang 的错误对象首先是**合法的 CogLang 表达式**，其次才是诊断事件。实现不得把用户输入、模型输出或执行期错误只表示为宿主语言异常而绕过 CogLang 层。

`v1.1.0` 冻结以下错误 Head 与最小 canonical 结构：

| 错误表达式 | 最小 canonical 结构 | 含义 |
|-----------|--------------------|------|
| `NotFound[]` | `NotFound[]` | 查询无结果、目标不存在、或不可合一 |
| `TypeError[...]` | `TypeError[op, param, expected, actual]` | 动态类型不匹配或参数值不满足运行时约束 |
| `PermissionError[...]` | `PermissionError[op, target]` | 权限不足、profile 禁止、或 capability 不满足 |
| `ParseError[...]` | `ParseError[reason, position]` | 解析失败 |
| `StubError[...]` | `StubError[op, message]` | 调用了已注册但当前未实现或未开放的能力 |
| `RecursionError[...]` | `RecursionError[op, depth, message]` | 递归或展开深度超限 |

上述最小结构是 canonical surface 的兼容性承诺；实现可以在 transport envelope 或诊断记录中附加更多字段，但不得改变这些 Head 的基本含义。

所有错误表达式都必须满足以下要求：

- 可以作为普通 CogLang 值进入后续表达式
- 可以出现在 `Trace` 与推理轨迹中
- 可以被 `Inspect`、`If`、`IfFound` 或等价机制消费
- 不得依赖宿主异常栈作为唯一可见信息源

### 8.2 诊断字段

当 parser、validator、executor 或 render 层生成诊断信息时，宿主侧诊断对象或 transport envelope **必须**支持以下字段名：

- `diagnostic_code`
- `phase`
- `source_span`
- `blame_object`
- `recoverability`
- `trace_policy`

字段约束如下：

- `diagnostic_code`：稳定的字符串代码。相同 profile 中不得把同一代码复用于不相容错误。
- `phase`：至少区分 `parse / validate / execute / render`。
- `source_span`：若诊断可定位到 canonical text，必须给出 1-based 起止位置；若无文本来源，可留空。
- `blame_object`：指向最相关的 `Head`、参数位、graph object ID、或外部 capability 名称。
- `recoverability`：描述调用方是否可通过分支、重试、降级、或能力切换继续推进；允许 profile 扩展具体取值集合。
- `trace_policy`：指示该诊断是否必须进入推理轨迹、仅在 trace 启用时记录、或仅写入宿主日志。

这些字段属于诊断契约，不要求全部编码进 canonical error expression 的参数位置。规范鼓励把“错误表达式”与“宿主诊断元数据”分层表示，而不是把所有上下文都塞进一个 Head 的位置参数里。

### 8.3 ParseError 与部分结构

Parser 遇到语法错误时，**不得**把宿主解析异常直接暴露为唯一结果；它必须返回 `ParseError[...]`，并在可恢复时附带部分结构信息。

`v1.1.0` 对 `ParseError` 的最小要求如下：

- canonical error expression 至少为 `ParseError[reason, position]`
- 若 parser 成功恢复了部分 AST，必须通过 transport envelope、诊断对象、或等价宿主接口暴露 `partial_ast` 或 `partial_ast_ref`
- 若无法恢复部分结构，可以省略 `partial_ast*` 字段，但不得伪造空 AST

保留部分结构的目的有二：

- 为训练期提供“部分正确”的结构反馈
- 为 UI / 调试器提供更精确的错误定位与修复建议

Readable Render 在展示 `ParseError` 时应同时体现：

- 失败原因
- 失败位置
- 已成功恢复的部分结构（若存在）

---

## 9. 可观测性与可读渲染

### 9.1 内置调试能力

`Trace`、`Assert`、`Explain` 是 CogLang 的内置调试与元观察能力，不是宿主系统后加的调试开关。

其边界如下：

- `Trace`：记录实际执行过的表达式轨迹，不改变返回值
- `Assert`：记录非致命异常状态，不替代错误传播
- `Explain`：返回计划预览，不执行目标表达式；在默认 profile 中可为 `StubError[...]`
- `Inspect`：保留的对象结构检视能力；若某实现提供该能力，它把对象结构作为数据返回，属于元认知/结构检视，但不替代 `Trace` 的时序记录，也不替代 `Explain` 的计划预览

因此，宿主实现可以在日志层面整合这些能力，但不得在语言语义上把它们折叠成同一个 operator。

CogLang 执行环境必须把这些调试事件接出到外部可观测性系统；`Observer` 只是推荐命名，等价 hook 亦可，但不得缺失这条桥接能力。

### 9.2 Trace Schema

`ReasoningTrace` 中的单条 CogLang 执行记录，最小字段如下：

| 字段 | 要求 |
|------|------|
| `expr_id` | 当前表达式在本次 trace 中的局部唯一标识 |
| `parent_id` | 父表达式 ID；顶层可为空 |
| `canonical_expr` | 被执行表达式的 canonical 形式 |
| `effect_class` | 对应 operator 的效果类别 |
| `result_summary` | 对返回值的稳定摘要；大对象可只记录摘要与引用 |
| `duration_ms` | 执行耗时，单位毫秒 |

以下字段为 `v1.1.0` 的推荐扩展字段：

- `source_span`
- `status`
- `trace_id`
- `parent_spans`
- `source_instance_id`

扩展字段约束：

- `source_span`：若表达式来自可定位文本，则应与 §8.2 的 `source_span` 协同
- `status`：推荐至少区分 `ok / error / stub / assertion_failed`
- `trace_id`：按需启用即可，不得默认作为所有消息或结果的常驻字段
- `parent_spans`：用于跨表达式或跨组件的溯源链拼接；若实现不支持 span 级追踪，可为空
- `source_instance_id`：为 P2 跨实例 trace 预留；P1 可为空

Trace 记录必须服务于两类消费方：

- 人类调试与审计
- 上层异常检测与统计汇总

因此，trace schema 可以裁剪大对象，但不得裁剪到无法判断“执行了什么、返回了什么、耗时多少”。

### 9.3 Readable Render 契约

每个合法的 CogLang 表达式都必须存在稳定的 Readable Render。Readable Render 是**人类展示层**，不是语义权威源，但它必须足够稳定，能支撑 trace、日志、UI 检查与人工审稿。

`v1.1.0` 对 Readable Render 的最低要求：

- 保留原始 `Head`
- 保留参数顺序
- 对嵌套表达式使用稳定缩进
- 对错误表达式展示错误 Head 与关键参数
- 对列表、字典、结构化结果对象使用稳定字段顺序
- 参考实现应提供 `to_readable()` 或等价接口

Readable Render **不得**：

- 隐式改写 canonical 结构
- 吞掉关键参数或错误字段
- 把不同 canonical 表达式渲染成不可区分的同一文本

Readable Render 的换行、缩进与 token 顺序只服务于显示和传输；它们不得被反向解释为图语义上的邻接顺序或层级顺序。

UI、日志和 trace 可以在 Readable Render 之外增加颜色、高亮、折叠、行号、或跳转锚点，但这些增强不得改变其可回溯到 canonical 表达式的能力。

---

## 10. 扩展与名称解析

### 10.1 名称解析模型

CogLang 的名称解析先冻结**抽象分发模型**，后冻结具体表面语法。

`v1.1.0` 中，名称解析涉及三类定义来源和一类执行提供方：

1. **静态内置 operator 定义**
2. **图内动态 operator 定义**
3. **运行时注册表条目**
4. **外部 adapter 提供者**

#### 1. 静态内置 operator 定义

指静态词表中注册、并由执行器原生提供语义的 operator 定义；其语法入口由对应 `operator head` 指向。

#### 2. 图内动态 operator 定义

指由 `Compose` 或等价图内机制注册到当前图谱作用域的 operator 定义；其语法入口由对应 `operator head` 指向。

#### 3. 运行时注册表条目

指不写入图谱、但由运行时注册表暴露给解析与执行层的 operator 定义条目。其目标是为：

- 插件化 operator
- 阶段性保留 operator
- 与 runtime bridge / adapter 绑定的 runtime capability

提供统一入口。

#### 4. 外部 adapter 提供者

指其最终行为由外部 adapter 提供的执行提供方。它们不单独参与名称优先级竞争；它们附着在某个已解析的 operator 定义或注册表条目之后提供实际执行能力。其执行可能需要：

- capability 检查
- 权限校验
- 外部系统联通性
- 运行时降级

### 10.2 解析顺序与冲突处理

在给定 validation context 中，每个**处于可执行位置的 `operator head`** **MUST** 解析到且仅解析到一个 operator 定义。

`term head` 与 `atom` 默认不参与本节的 operator 解析流程；它们是否被允许出现，以及是否被某个 operator 作为结构化项消费，由对应条目决定。

#### 未显式限定名称时的默认解析顺序

1. 静态内置 operator 定义
2. 图内动态 operator 定义
3. 运行时注册表条目

默认情况下，静态内置 Head **不可**被后续层覆盖。

#### 显式限定名称

`v1.1.0` 冻结“支持显式限定名称”这一抽象能力，但**不在本版本冻结具体分隔符写法**。

也就是说：

- 规范允许未来存在“限定名”
- 但不预先承诺其表面拼写一定是某个具体符号形式
- 因而这项能力当前是面向实现者和架构文档的保留位，而不是面向普通使用者的可教学语法

#### 冲突处理

- 同一解析层内的重复注册必须在注册阶段报错
- 图内动态 operator 定义与运行时注册表条目同名时，未限定名称默认解析到图内动态定义
- 显式限定名称一旦被采用，必须跳过无关层的 shadowing 规则

#### 未解析与不可用的错误语义

- 语法合法但名称未解析：**验证失败**，不得进入执行阶段
- 名称已解析但实现未安装：`StubError[head, "operator_unavailable"]`
- 名称已解析但 capability 不足：`PermissionError[head, capability]`

名称解析失败与语法解析失败属于不同问题。除非某个实现将二者封装在同一宿主诊断对象中，否则名称未解析不应被表述为 `ParseError[...]`。

此类失败不是 CogLang 运行时值；宿主 validator **MUST** 至少报告：

- `head`
- `attempted_resolution_scopes`
- `source_span`
- `diagnostic_code`

### 10.3 扩展能力边界

每个注册表 operator 或外部 adapter 绑定条目至少必须声明：

- canonical name
- status
- layer
- arity / signature
- effect class
- determinism
- required capabilities
- default unavailable behavior
- readable render hint

#### capability 声明

若某个 operator 需要外部能力，规范当前仅冻结“存在 capability 标识符”这一机制；具体 capability 名称在 `v1.1.0` 中为 `implementation-defined`，但 profile manifest **MUST** 公布精确字符串。

实现建议至少区分：

- `graph_write`
- `trace_write`
- `external_io`
- `cross_instance`
- `self_modify`

能力检查失败时，必须返回 `PermissionError[...]`，而不是静默降级。

#### 外部副作用

凡效果类别含 `external` 的 operator：

- 必须显式声明其外部副作用
- 必须声明是否允许在默认 profile 下调用
- 必须进入 trace

凡未声明外部副作用的 operator，不得在执行时隐式访问外部系统。

---

## 11. 当前特性清单与状态记录

### 11.1 Core

当前草案中已按 `Core` 收口的能力包括：

- 四层表示模型：`AST / canonical text / readable render / transport envelope`
- 图优先语言身份与显式写图边界
- 错误是值的基本模型，以及 `NotFound / TypeError / PermissionError / ParseError / StubError / RecursionError`
- 核心值类型：`String / Number / Bool / List / Dict / ErrorExpr`
- 公开知识图谱主节点类型：`Entity / Concept / Rule / Meta`
- `Abstract` 的“原型提取 + 触发”语义，以及其 provenance 约束
- `Equal`
- `Compare`
- `Unify`
- `Match`
- `Get`
- `Query` 的三参数接口、`k` / `mode` 分离、默认 `mode`
- `AllNodes`
- `Traverse`
- `ForEach`
- `Do`
- `If`
- `IfFound`
- `Compose`
- `Create`
- `Update`
- `Delete`
- `Trace`
- `Assert`
- Readable Render 最低契约
- 名称解析的抽象分发模型与默认优先级

### 11.2 Reserved

当前草案中作为 `Reserved` 保留、但未要求默认实现的能力包括：

- `Explain`
- `Inspect`
- 非默认 `Query.mode`
- 查询 `cost / gain` 相关元推理接口
- 规则候选 envelope
- 规则发布、验证、回滚链的完整 schema
- 显式限定名称的具体表面语法
- 更完整的跨实例 trace 字段集与跨组件溯源拼接细节

### 11.3 Experimental

当前仅作为 `Experimental` 议题记录、尚未进入稳定规范的方向包括：

- 通用 `Recover[...]` 风格恢复语法
- 更强的自检 / 自修改 operator
- 更强的类型标注与泛型系统
- 语法糖（如局部绑定、管道等）
- 高风险、强宿主耦合的 adapter 专用能力

### 11.4 `Baseline / Enhanced` Profiles

`v1.1.0` 建议至少区分以下两类 profile：

- `Baseline`：默认基线 profile，用于承载图优先主链、最小组合能力、基础诊断与可观测性、以及当前 `Core` 的最低一致性要求
- `Enhanced`：增强 profile，用于承载扩展 operator、非默认查询模式、受控外部能力、以及仍不适合进入 `Core` 主干的增强执行能力

这两类 profile 的关系约束如下：

- `Enhanced` **MUST** 保持对 `Baseline` 兼容性表面的兼容，不得破坏既有 `Core`
- 某能力若只在 `Enhanced` 中可用，其条目 **MUST** 在 `Baseline Availability` 中明确写出 profile 条件
- `Baseline` 不应承载高风险、强宿主耦合、或架构级协议能力
- `Enhanced` 可以承载更强的扩展执行能力，但这些能力默认仍不等于“可自动入图”、“程序执行域”、或“已成为公开知识层对象”

当前建议的收口方式是：

- `Baseline`：`Abstract / Equal / Compare / Unify / Match / Get / Query / AllNodes / Traverse / If / IfFound / Do / ForEach / Compose / Create / Update / Delete / Trace / Assert` 及其相关基础模型
- `Enhanced`：更强的 `Query.mode`、`Explain`、`Inspect`、`cost / gain` 元推理接口、扩展注册表 operator、受控外部能力、以及其他仍不适合进入 `Core` 的增强执行能力

Profile 是执行可用性与能力打包边界，不是新的语言层级；其作用是承接复杂度压力，而不是改写 `Core` 语义主干。

### 11.5 与 §1.4 的关系

本章不重复定义晋升 / 降级规则；权威规则见 `§1.4`。

本章只负责记录当前版本中哪些能力处于：

- `Core`
- `Reserved`
- `Experimental`

以及它们的当前状态说明、备注和引用位置。

---

## 12. 一致性测试与参考实现边界

### 12.1 Conformance Suite

`Conformance Suite` 的目标不是覆盖所有实现细节，而是验证实现是否遵守规范冻结的兼容性表面。

`v1.1.0` 至少应包含以下测试组：

- parser / validator 测试：语法、变量位置、名称解析、诊断字段
- canonical round-trip 测试：`AST <-> canonical text`
- execution 测试：核心 operator 的正常值、错误值、边界值
- graph-write boundary 测试：显式写图与禁止隐式图化
- error propagation 测试：默认传播与显式阻断点
- trace 测试：`Trace` / `Assert` 的最小字段与值透明语义
- rendering 测试：readable render 的稳定输出
- extension 测试：注册表条目、未安装实现、capability 失败

测试通过的判据应优先依赖规范声明的字段和语义，而不是依赖某个具体实现的内部数据结构。

### 12.2 Golden Examples

每个进入 `Core` 的 operator 至少应配套以下 example 类型：

- 正例：典型成功路径
- 边界例：空列表、空图、最小参数、`k=0` 等边界输入
- 错误例：类型不匹配、权限不足、名称未解析、留桩能力
- trace 例：至少一条可验证 `Trace` / `Assert` 字段的样例

以下主题必须有单独的 golden example：

- `Abstract` 不直接生成规则
- `Query` 的 `k` 与 `mode` 解耦
- 显式写图边界与禁止隐式图化
- `ParseError` 与 `partial_ast`
- Readable Render 与 canonical text 的非同一性
- `Operation` 作为 executor 内部载体时的对外标注方式

本规范的展开样例集见伴随文档 `CogLang_Conformance_Suite_v1_1_0.md`。其中以下样例 ID 应被视为本版最小权威样例索引：

- `GE-001`：`operator head` 与 `term head` 的区分
- `GE-002`：canonical text 与多行 readable render 的非同一性
- `GE-003`：`Query` 基本成功路径
- `GE-004`：`Query.k` 的最小语义
- `GE-005`：`Abstract` 只做原型提取与触发
- `GE-006`：`Trace` 的值透明与最小 trace 字段
- `GE-007`：`Assert` 的非致命语义
- `GE-008`：`ParseError` 与 `partial_ast`
- `GE-009`：名称未解析属于 validator 诊断，不等同于 `ParseError`
- `GE-010`：`Operation` 作为 executor 内部载体时的对外标注
- `GE-018`：`Explain` 在 `Baseline` 中的默认留桩
- `GE-019`：extension-backed operator 的 capability denied
- `GE-020`：名称已解析但实现未安装
- `GE-021`：`If` 对自动传播错误值的条件分支处理
- `GE-022`：`IfFound` 对 `NotFound[]`、错误值与 `List[]` 的分流
- `GE-023`：`ForEach` 的稳定映射与结果保留
- `GE-024`：`Do` 的顺序执行与非自动中止
- `GE-025`：`Inspect` 在 `Baseline` 中的默认留桩
- `GE-026`：`IfFound` 的 bind-and-continue 惯用法
- `GE-027`：`AllNodes` 的可见性与稳定顺序
- `GE-028`：`Update` 的成功路径与 `confidence=0` 拒绝
- `GE-029`：`Delete` 的 soft-delete 与幂等性
- `GE-030`：`ForEach` 对 body 错误的结果保留
- `GE-031`：`Get` 的 `Dict / List / node_attr` 三路分派
- `GE-032`：`Create` 缺省 ID 的唯一分配与返回一致性
- `GE-033`：`Create["Edge", ...]` 的 alias 归一化早于内部引用校验

### 12.3 参考实现边界

参考实现应覆盖以下最小能力：

- parser
- validator
- canonical serializer
- readable renderer
- 核心 error model
- `Core` operator 的最小可执行语义

以下内容不要求由参考实现完整覆盖：

- runtime bridge 内部算法
- SoftGraphMemory 内部物理实现
- Observer 后端的具体日志系统
- 外部 adapter 的真实网络或插件执行
- `Reserved / Experimental` 能力的完整行为

规范约束关注的是：输入输出语义、诊断字段、trace 字段、名称解析规则、以及兼容性表面。实现优化可以自由变化，但不得破坏这些外部可观察契约。

---

## 13. 非目标与延后事项

以下内容不属于 `v1.1.0` 的目标：

- 把 CogLang 优化成面向人类手写的通用编程语言
- 为了语法简洁而引入大量等价写法
- 把所有 runtime metadata 都提升为核心语法
- 在语言规范中冻结 runtime bridge、宿主传输层或外部 adapter 的完整协议
- 把原始结构层、规范表示层、输出解释层重新压成一层
- 把 `Reserved` 条目写成看似可稳定依赖的 `Core` 能力

延后事项包括但不限于：

- 更强的元认知 operator
- 更完整的规则候选 / 发布 / 回滚对象模型
- 应用侧生命周期对象模型与持久化提交协议
- 更强类型系统
- 更丰富的语法糖
- `P3/P4` 方向的程序性语法与程序执行域能力
- 跨实例 trace / provenance 的完整对象模型
- capability manifest 与 adapter catalog 的细化

---

## 附录 A：Operator 规格模板

```text
Operator: <name>
Status: Core | Reserved | Experimental
Layer: language | executor | runtime_bridge | observability | adapter
Syntax & Signature: <sig>
Validator Constraints: <validator rules>
Return Contract: <normal return and failure contract>
Effect Class: pure | graph-read | graph-write | meta | diagnostic | external
Determinism: deterministic | graph-state-dependent | model-dependent | implementation-defined
Semantics: <normative behavior>
Baseline Availability: <正常执行 | StubError | PermissionError | profile-specific availability>
Observability: <trace/log requirements>
Compatibility: <name frozen? semantics frozen?>
Notes: <informative notes>
```

## 附录 B：语言规范后续补写优先级

建议优先补写顺序：

1. 查询 operator 的 `k / mode` 设计
2. 扩展与名称解析模型
3. `Explain` / trace schema
4. Reserved / Experimental 清单
5. grammar 与 conformance suite
6. rendering / UI contract 的同步细化
