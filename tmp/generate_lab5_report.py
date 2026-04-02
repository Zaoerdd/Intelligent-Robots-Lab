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
            "This report summarizes the final Lab 5 results for the <font name='Courier'>limo</font> vehicle, "
            "including workspace build, RViz model display, Ackerman-mode Gazebo simulation, camera projection, "
            "lane detection, and lane-following control.",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("1. Objectives", styles["Heading2"]))
    story.append(
        Paragraph(
            "1. Build the <font name='Courier'>limo_ws</font> workspace and compile the simulation packages.<br/>"
            "2. Display the LIMO model in RViz and run Ackerman-mode Gazebo simulation.<br/>"
            "3. Review the available robot control methods.<br/>"
            "4. Run the camera projection, lane detection, and control pipeline.",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("2. Environment", styles["Heading2"]))
    story.append(
        Paragraph(
            "Remote host: <font name='Courier'>ubuntu@192.168.40.128</font><br/>"
            "Operating system: Ubuntu 20.04<br/>"
            "ROS version: <font name='Courier'>noetic</font><br/>"
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

    story.append(Paragraph("3. RViz Model Display", styles["Heading2"]))
    story.append(
        Paragraph(
            "The LIMO URDF model was loaded in RViz with <font name='Courier'>display_models.launch</font>. "
            "The screenshot below shows the robot model and the default RViz display configuration.",
            styles["BodySmall"],
        )
    )
    story.append(fit_image(GENERATED / "manual_model_display.png", 16.2, 9.6))
    story.append(Paragraph("Figure 1. Manual screenshot of RViz model display.", styles["BodySmall"]))

    story.append(Paragraph("4. Ackerman Simulation", styles["Heading2"]))
    story.append(
        Paragraph(
            "The Ackerman-mode simulation was started with <font name='Courier'>roslaunch limo_gazebo_sim limo_ackerman.launch</font>. "
            "The screenshot below shows Gazebo and RViz running together.",
            styles["BodySmall"],
        )
    )
    story.append(
        Preformatted(
            "/controller_spawner\n"
            "/gazebo\n"
            "/gazebo_gui\n"
            "/robot_state_publisher\n"
            "/rviz\n"
            "\n"
            "Verified topics:\n"
            "/cmd_vel\n"
            "/limo/scan\n"
            "/limo/color/image_raw\n"
            "/limo/depth/image_raw\n"
            "/limo/imu\n"
            "/tf",
            styles["CodeBlock"],
        )
    )
    story.append(fit_image(GENERATED / "manual_ackerman_sim.png", 17.0, 9.4))
    story.append(Paragraph("Figure 2. Manual screenshot of Ackerman-mode simulation in RViz and Gazebo.", styles["BodySmall"]))

    story.append(Paragraph("5. Control Methods", styles["Heading2"]))
    story.append(
        Paragraph(
            "The lab material introduced two standard control methods for the simulated robot: "
            "<font name='Courier'>rqt_robot_steering</font> and keyboard teleoperation.",
            styles["BodySmall"],
        )
    )
    story.append(
        Preformatted(
            "rosrun rqt_robot_steering rqt_robot_steering\n"
            "rosrun teleop_twist_keyboard teleop_twist_keyboard.py",
            styles["CodeBlock"],
        )
    )

    story.append(Paragraph("6. Camera Projection", styles["Heading2"]))
    story.append(
        Paragraph(
            "The projection pipeline was launched with <font name='Courier'>extrinsic_camera_calibration.launch</font>. "
            "The projected image was observed in <font name='Courier'>rqt Image View</font> on "
            "<font name='Courier'>/camera/image_projected_compensated</font>.",
            styles["BodySmall"],
        )
    )
    story.append(fit_image(GENERATED / "manual_projected_view.png", 17.0, 10.0))
    story.append(Paragraph("Figure 3. Manual screenshot of the projected camera view.", styles["BodySmall"]))

    story.append(Paragraph("7. Lane Detection and Control", styles["Heading2"]))
    story.append(
        Paragraph(
            "The lane-detection demo was launched with <font name='Courier'>detect_lane.launch</font>, and the "
            "lane-following controller was started with <font name='Courier'>turtlebot3_autorace_control_lane.launch</font>. "
            "The screenshot below shows the detected lane image displayed in <font name='Courier'>rqt Image View</font>.",
            styles["BodySmall"],
        )
    )
    story.append(
        Preformatted(
            "Verified topic chain:\n"
            "/camera/image_projected_compensated\n"
            "/detect/image_lane/compressed\n"
            "/detect/lane\n"
            "/cmd_vel\n"
            "\n"
            "Runtime checks:\n"
            "- /detect/lane published std_msgs/Float64\n"
            "- /control_lane subscribed to /detect/lane\n"
            "- /control_lane published /cmd_vel\n"
            "- /gazebo subscribed to /cmd_vel\n"
            "- sample /detect/lane value: -163.10505252446842",
            styles["CodeBlock"],
        )
    )
    story.append(fit_image(GENERATED / "manual_detect_lane.png", 17.0, 10.0))
    story.append(Paragraph("Figure 4. Manual screenshot of the lane-detection result.", styles["BodySmall"]))

    story.append(Paragraph("8. Runtime Fix", styles["Heading2"]))
    story.append(
        Paragraph(
            "During the first live run of <font name='Courier'>detect_lane.launch</font>, the original node raised "
            "<font name='Courier'>AttributeError: 'DetectLane' object has no attribute 'mov_avg_left'</font>. "
            "A minimal fix was applied by initializing the lane-fit state and moving-average buffers, and by adding "
            "guards before averaging empty history arrays. After the fix, the lane-detection and controller nodes ran correctly.",
            styles["BodySmall"],
        )
    )
    story.append(
        Preformatted(
            "Patched local file:\n"
            "LAB5/generated/detect_lane_fixed.py",
            styles["CodeBlock"],
        )
    )

    story.append(Paragraph("9. Conclusion", styles["Heading2"]))
    story.append(
        Paragraph(
            "Lab 5 was completed successfully. The workspace was built, the LIMO model was displayed in RViz, "
            "Ackerman-mode simulation ran in Gazebo, the projected camera image was verified, and the lane-detection "
            "pipeline was brought up end-to-end. This final report uses manually captured screenshots from the real experiment "
            "and includes the runtime verification and the minimal code fix required for a stable lane-detection run.",
            styles["BodySmall"],
        )
    )

    doc.build(story)
    print(OUT_PDF)


if __name__ == "__main__":
    build_pdf()
