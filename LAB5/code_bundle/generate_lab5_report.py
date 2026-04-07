from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, Preformatted, SimpleDocTemplate, Spacer


ROOT = Path(r"D:\Intelligent-Robots-Lab\LAB5")
GENERATED = ROOT / "generated"
OUT_PDF = ROOT / "LAB5_report.pdf"


def fit_image(path: Path, max_width_cm: float, max_height_cm: float) -> Image:
    with PILImage.open(path) as img:
        width, height = img.size
    max_width = max_width_cm * cm
    max_height = max_height_cm * cm
    scale = min(max_width / width, max_height / height)
    return Image(str(path), width=width * scale, height=height * scale)


def build_pdf() -> None:
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BodySmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodeBlock",
            parent=styles["BodyText"],
            fontName="Courier",
            fontSize=8.3,
            leading=10.5,
            backColor=colors.whitesmoke,
            borderPadding=6,
            borderWidth=0.4,
            borderColor=colors.lightgrey,
            spaceAfter=10,
        )
    )

    title = styles["Title"]
    title.fontName = "Helvetica-Bold"
    title.fontSize = 18
    title.leading = 22

    story = []
    story.append(Paragraph("CS401 Intelligent Robotics Lab 05 Report", title))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Date: 2026-04-01", styles["BodySmall"]))
    story.append(
        Paragraph(
            "This report summarizes the setup and validation of the <font name='Courier'>limo</font> "
            "vehicle simulation in ROS Noetic, including RViz/Gazebo workflow, control methods, "
            "and the lane-detection demo pipeline.",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("1. Objectives", styles["Heading2"]))
    story.append(
        Paragraph(
            "1. Build the <font name='Courier'>limo_ws</font> workspace and compile the simulation packages.<br/>"
            "2. Display the LIMO model in RViz and start Ackerman-mode Gazebo simulation.<br/>"
            "3. Review control methods such as <font name='Courier'>rqt_robot_steering</font> and keyboard teleoperation.<br/>"
            "4. Run the camera projection, lane detection, and lane-following control pipeline.",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("2. Environment", styles["Heading2"]))
    story.append(
        Paragraph(
            "Remote host: <font name='Courier'>ubuntu@192.168.40.128</font><br/>"
            "Remote OS: Ubuntu 20.04<br/>"
            "ROS distro: <font name='Courier'>noetic</font><br/>"
            "Workspace: <font name='Courier'>/home/ubuntu/limo_ws</font><br/>"
            "Repository: <font name='Courier'>ugv_gazebo_sim</font>",
            styles["BodySmall"],
        )
    )
    story.append(
        Preformatted(
            "mkdir -p ~/limo_ws/src\n"
            "cd ~/limo_ws/src\n"
            "git clone https://github.com/Intelligent-Robot-Course/ugv_gazebo_sim.git\n"
            "cd ~/limo_ws\n"
            "rosdep install --from-paths src --ignore-src -r -y\n"
            "catkin_make",
            styles["CodeBlock"],
        )
    )
    story.append(
        Paragraph(
            "The workspace was built successfully on the remote Ubuntu machine before the runtime checks below were performed.",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("3. Launch Validation", styles["Heading2"]))
    story.append(
        Preformatted(
            "ROS_DISTRO=noetic\n"
            "roslaunch --files limo_description display_models.launch\n"
            "roslaunch --files limo_gazebo_sim limo_ackerman.launch\n"
            "roslaunch --files limo_gazebo_sim limo_demo.launch\n"
            "roslaunch --files limo_camera extrinsic_camera_calibration.launch\n"
            "roslaunch --files limo_detect detect_lane.launch\n"
            "roslaunch --files limo_driving turtlebot3_autorace_control_lane.launch",
            styles["CodeBlock"],
        )
    )
    story.append(
        Paragraph(
            "All required launch files resolved correctly during this session. The detailed node/topic summary is saved in "
            "<font name='Courier'>lab5_validation_summary.txt</font>.",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("4. RViz and Gazebo Workflow", styles["Heading2"]))
    story.append(
        Paragraph(
            "The reference workflow from the supplied lab material is shown below. These figures document the expected "
            "RViz model display and Ackerman-mode Gazebo scene. In parallel, the live session verified that Gazebo "
            "published <font name='Courier'>/cmd_vel</font>, <font name='Courier'>/limo/scan</font>, and "
            "<font name='Courier'>/limo/color/image_raw</font>, with RViz subscribing to the sensor topics.",
            styles["BodySmall"],
        )
    )
    story.append(fit_image(GENERATED / "ref_rviz_model.png", 15.8, 9.4))
    story.append(Paragraph("Figure 1. Reference RViz model-display result from the provided Lab 5 material.", styles["BodySmall"]))
    story.append(fit_image(GENERATED / "ref_ackerman_gazebo.png", 15.8, 9.1))
    story.append(Paragraph("Figure 2. Reference Ackerman-mode Gazebo result from the provided Lab 5 material.", styles["BodySmall"]))
    story.append(
        Preformatted(
            "/controller_spawner\n"
            "/gazebo\n"
            "/gazebo_gui\n"
            "/robot_state_publisher\n"
            "/rviz\n"
            "\n"
            "/clock\n"
            "/cmd_vel\n"
            "/limo/color/image_raw\n"
            "/limo/depth/image_raw\n"
            "/limo/imu\n"
            "/limo/scan\n"
            "/tf",
            styles["CodeBlock"],
        )
    )

    story.append(Paragraph("5. Control Methods", styles["Heading2"]))
    story.append(
        Paragraph(
            "The lab introduces two basic ways to move the robot: the GUI-based "
            "<font name='Courier'>rqt_robot_steering</font> panel and keyboard teleoperation. "
            "The figures below are reference screenshots from the supplied lab material.",
            styles["BodySmall"],
        )
    )
    story.append(fit_image(GENERATED / "ref_rqt_robot_steering.png", 10.6, 6.4))
    story.append(Paragraph("Figure 3. Reference rqt_robot_steering interface.", styles["BodySmall"]))
    story.append(fit_image(GENERATED / "ref_keyboard_control.png", 12.0, 6.6))
    story.append(Paragraph("Figure 4. Reference keyboard-control result.", styles["BodySmall"]))

    story.append(Paragraph("6. Lane-Detection Demo", styles["Heading2"]))
    story.append(
        Paragraph(
            "For the autorace-style demo, the race world was started with "
            "<font name='Courier'>limo_demo.launch</font>, then the camera projection, lane detection, "
            "and lane-following controller were launched on top of the Gazebo simulation. "
            "The live topic chain was verified as "
            "<font name='Courier'>/camera/image_projected_compensated -> /detect/image_lane/compressed -> /detect/lane -> /cmd_vel</font>.",
            styles["BodySmall"],
        )
    )
    story.append(fit_image(GENERATED / "ref_demo_world.png", 15.4, 8.7))
    story.append(Paragraph("Figure 5. Reference demo world from the provided Lab 5 material.", styles["BodySmall"]))
    story.append(fit_image(GENERATED / "live_projected_image.png", 14.8, 7.5))
    story.append(Paragraph("Figure 6. Live projected camera image saved from /camera/image_projected_compensated.", styles["BodySmall"]))
    story.append(fit_image(GENERATED / "live_detect_lane.jpg", 14.8, 7.5))
    story.append(Paragraph("Figure 7. Live lane-detection result saved from /detect/image_lane/compressed.", styles["BodySmall"]))
    story.append(
        Preformatted(
            "Type: std_msgs/Float64\n"
            "Topic: /detect/lane\n"
            "Publisher: /detect_lane\n"
            "Subscriber: /control_lane\n"
            "\n"
            "Type: geometry_msgs/Twist\n"
            "Topic: /cmd_vel\n"
            "Publisher: /control_lane\n"
            "Subscriber: /gazebo\n"
            "\n"
            "sample /detect/lane value: -163.10505252446842",
            styles["CodeBlock"],
        )
    )

    story.append(Paragraph("7. Runtime Fix", styles["Heading2"]))
    story.append(
        Paragraph(
            "During the first live run of <font name='Courier'>detect_lane.launch</font>, the original node crashed with "
            "<font name='Courier'>AttributeError: 'DetectLane' object has no attribute 'mov_avg_left'</font>. "
            "A minimal fix was applied by initializing the lane-fit state and moving-average arrays, and by guarding "
            "the averaging step when the history buffers are still empty. After this fix, the lane-detection and "
            "control nodes ran without the previous callback error.",
            styles["BodySmall"],
        )
    )
    story.append(
        Preformatted(
            "Patched file:\n"
            "/home/ubuntu/limo_ws/src/ugv_gazebo_sim/limo/limo_detect/nodes/detect_lane\n"
            "\n"
            "Saved local copy:\n"
            "LAB5/generated/detect_lane_fixed.py",
            styles["CodeBlock"],
        )
    )

    story.append(Paragraph("8. Conclusion", styles["Heading2"]))
    story.append(
        Paragraph(
            "Lab 5 was reproduced successfully on the remote Ubuntu machine. The workspace was built, the LIMO "
            "simulation launch chain was validated, and the camera-projection and lane-detection pipeline was brought "
            "up end-to-end. The final report combines the provided workflow references with live validation evidence "
            "and live ROS-generated result images from the current session.",
            styles["BodySmall"],
        )
    )

    doc.build(story)
    print(OUT_PDF)


if __name__ == "__main__":
    build_pdf()
