# 任务说明
逐个读取并启动完成下面的任务，跳过[x]的任务，每个任务完成后，刷新todo.md文件，将[]替换为[x]

# 任务清单
- [x] 基于venv环境，创建自动install脚本，用于安装项目依赖；遇到需要下载模型的，自动下载模型到合适的位置。
- [x] 基于venv环境，创建自动run_host以及自动run_client脚本，用于启动项目.
- [x] 项目根目录下创建run_host.sh以及run_client.sh脚本，用于启动项目. 打开终端执行run_host.sh即可启动host服务器，执行run_client.sh启动client客户端，自行验证install、run_host.sh、run_client.sh是否正常运行
- [x] 检查plan.md文件，确认所有任务是否完成，没有遗漏
- [x] 完成所有测试，确保所有功能正常运行，没有错误；任何没有完成的测试，都需要修复，即使是预期失败的测试也需要修复；缺少的依赖需要安装，确保所有依赖都能正常安装，确保所有python都依赖于venv环境。