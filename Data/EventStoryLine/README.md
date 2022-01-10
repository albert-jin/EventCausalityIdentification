## Event StoryLine

Caselli等人【1】 2017 
Event StoryLine 中三大子任务之一：Explanatory Relation Identification and Classification 选择时序或逻辑相关的事件对进行关系分类

定义为事件之间的一种松散的因果或时序关系，一件事的提及解释了/证明了另一件事的发生

关系包含：时序关系 TLINK、 因果关系 PLOT_LINK、

因果关系PLOT_LINK 包含: 可分为 FALLING_ACTION（直接的推测和结论，事件是另一事件的（预期的）结果或影响） 和 PRECONDITION（事件间接的引起导致另一事件）



original link: https://github.com/tommasoc80/EventStoryLine

our resource link（迅雷云盘）:
链接：https://pan.xunlei.com/s/VMt21IQr5sp6OvhVI-kYyhMKA1 提取码：23qp

original link 中提供了许多不相关任务的标注信息，因此不建议使用，且Liu等人【2】2020的工作相关的公开代码(代码地址：https://github.com/jianliu-ml/EventCausalityIdentification) 对EventStoryLine的处理太多繁杂，也不建议使用





下载本云盘文件后，解压到当前README.md所在同级文件夹中，并运行ECB+_preprocess.py 提取事件因果数据集，
不出意料的话，将提取出 共有 6721 条数据


[1] Caselli T, Vossen P. The event storyline corpus: A new benchmark for causal and temporal relation extraction[C]//Proceedings of the Events and Stories in the News Workshop. 2017: 77-86.

[2] Jian Liu, Yubo Chen, and Jun Zhao. 2020. Knowledge enhanced event causality identification with mention masking generalizations. In Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence, 2020, pages 3608–3614. ijcai.org.