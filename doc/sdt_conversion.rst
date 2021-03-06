SDT 在翻译过程的约定
===============================

实现了L属性的翻译方案。在执行翻译的过程中对输入元素进行求值。

- 语法栈存储一个元素，包含了当前状态，和元素的属性。
- 对输入的Token(包含了Terminal或者Value),它的值返回为语法栈中元素的综合属性值。
- 对规约的Code，它返回一个单独的求值语法栈元素。

Production 产生式规则的约定
--------------------------------------------------

Production 不需要另外约定一个Rule为求值。它规约的求值隐含到一个系列规则中：

- 规约的最后一个对象如果是Code类型，就把它作为规约后符号的值。
- 规约的最后一个对象如果不是 Code，就把第一个元素的值作为符号的值（默认）
- 如果规约的产生式是空产生式，那它就是一个Code对象，就对这个对象的code属性进行求值，
  并将结果作为符号的值。

Code内代码对产生式的元素引用在生成产生式之前的替换
------------------------------------------------------------

Code对象的体{{ }}内可以以 {n} 的方式引用，作为继承属性。但是不能引用产生式体位于后面的对象。 ::

    P   :==  A  {{ inh = {0}.label; val={1}.code }}  B  {{ code = "label" {0}.label + {3}.code }}
    {0}     {1}             {2}                     {3}

loader要计算出引用者和被引用者在栈之间的关系并替换为一个栈的索引值（在这里是一个Stack列表）。 ::

    P   :==  A  {{ inh = Stack[-2].label; val=Stack[-1].label }} B {{ code = "label" + Stack[-4].label + Stack[-1].code }}

Stack 是由 ``sdt.env.update({'Stack':sdt.state_stack})`` 引入求值环境。
索引的值为当前栈到目标引用的距离。

最后一个 ``{{rule}}`` 里面的变量作为产生式 ``P`` 的综合属性。


求值过程
-----------------

- 求值用exec展开。
- sdt.env 作为求值的全局环境。
- 将语法栈stack加入到env中，用 ``Stack`` 作为变量名。
- 建立一个临时的local环境，求值完成后用 **Prop** 将所有的属性打包到 ``__dict__``.
  放入栈中，这样就可以从其他栈直接引用属性。


产生式翻译方案的语法
--------------------------------------------------

- 可以左递归
- 不能使用空产生式，原因
    - 会产生位置替换问题。
    - 空产生式形式留给了翻译方案的代码块。
    - 理论上应该可以实现，不过留给后面练习，这里没有特别的必要性。
- 可以使用代码块。
- 可以在产生式第一个位置使用代码块。

代码块 Code 语法 {{rule}}
--------------------------
- 代码块内语句使用python的 ``simple_stmt`` 。也可以调用定义区的函数。
- 可以跨行
- 短句后面的 ``;`` 可以省略，也可以写上
- 不可以使用 ``compound_stmt`` , 这种语句可以到语法规则区rules part定义。
- rule 里面不能使用字典的花括号，因为它是以字符串传递到编译程序，
  在过程中会被format一次， 加入花括号会导致格式化失败。所以 ``d = {'a': 1, 'b': 2}``
  要使用列表语法 ``d = dict([('a', 1), ('b',2)])``

边规约边翻译的方案
---------------------------------------

相对于先规约语法树，再进行翻译，这里先采用边规约边翻译。因为方案对应的便利性。

未来对于语法树方案进行研究。


