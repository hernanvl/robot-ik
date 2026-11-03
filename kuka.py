import pybullet as p
import pybullet_data
import time
import numpy as np

# Connect to PyBullet GUI
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)

# Load ground and robot
plane_id = p.loadURDF("plane.urdf")
robot_id = p.loadURDF("kuka_iiwa/model.urdf", useFixedBase=True)

# Load a cube on the floor
#cube_pos = [0.268, 0.629, 0.01]  # X, Y, Z position (slightly higher for visibility)
cube_pos = np.load("cube_pos.npy")

cube_id = p.loadURDF("cube_small.urdf", basePosition=cube_pos)
p.changeVisualShape(cube_id, -1, rgbaColor=[1, 0, 0, 1])

# Get end-effector index (KUKA iiwa's last link)
end_effector_index = 6
num_joints = 7  # KUKA iiwa has 7 joints


p.resetDebugVisualizerCamera(
    cameraDistance=1.5,
    cameraYaw=45,
    cameraPitch=-30,
    cameraTargetPosition=cube_pos
)


# Target position - MATCH the cube position (slightly above it)
target_pos = [cube_pos[0], cube_pos[1], cube_pos[2] + 0.1] # Hovering above the cube

print(f"Cube position: {cube_pos}")
print(f"Target position: {target_pos}")

# Run simulation loop with continuous IK updates
for step in range(2000):
    # Calculate IK for current target
    joint_angles = p.calculateInverseKinematics(
        robot_id, 
        end_effector_index, 
        target_pos,
        maxNumIterations=100,
        residualThreshold=0.001
    )
    
    # Apply joint control only to the actual joints
    for i in range(num_joints):
        p.setJointMotorControl2(
            bodyIndex=robot_id,
            jointIndex=i,
            controlMode=p.POSITION_CONTROL,
            targetPosition=joint_angles[i],
            force=200,
            maxVelocity=1.0
        )
    
    p.stepSimulation()
    time.sleep(1./240.)
    
    # Print end-effector position every 100 steps
    if step % 100 == 0:
        ee_state = p.getLinkState(robot_id, end_effector_index)
        ee_pos = ee_state[0]
        print(f"Step {step}: End-effector at {[f'{x:.3f}' for x in ee_pos]}")

# Keep GUI open
print("Target reached! Press Ctrl+C to exit.")
while True:
    p.stepSimulation()
    time.sleep(1./240.)

