import mujoco
import mujoco.viewer

# 指向官方的右手场景模型
xml_path = "Software/sim_rl/simulation/mujoco/scene_right.xml"

# 加载模型和数据
model = mujoco.MjModel.from_xml_path(xml_path)
data = mujoco.MjData(model)

print("🚀 正在启动 MuJoCo 仿真环境，按 ESC 退出...")
mujoco.viewer.launch(model, data)