from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(r"D:\Intelligent-Robots-Lab\LAB4")
GENERATED = ROOT / "generated"
OUT_PDF = ROOT / "LAB4_report.pdf"


def fit_image(path: Path, max_width_cm: float, max_height_cm: float) -> Image:
    with PILImage.open(path) as img:
        width, height = img.size
    max_width = max_width_cm * cm
    max_height = max_height_cm * cm
    scale = min(max_width / width, max_height / height)
    return Image(str(path), width=width * scale, height=height * scale)


def build_pdf():
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
            fontSize=8.5,
            leading=11,
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
    story.append(Paragraph("CS401 Intelligent Robotics Lab 04 Report", title))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Date: 2026-03-31", styles["BodySmall"]))
    story.append(
        Paragraph(
            "This report summarizes the final results of Lab 4, including TurtleBot3 Gazebo simulation, "
            "multi-computer interaction, and camera calibration.",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("1. Objectives", styles["Heading2"]))
    story.append(
        Paragraph(
            "1. Run TurtleBot3 in Gazebo and visualize camera and LiDAR data in RViz.<br/>"
            "2. Verify multi-computer interaction by running the robot side on the remote Ubuntu machine and "
            "running keyboard control on the local machine.<br/>"
            "3. Understand camera calibration and obtain calibrated camera parameters.",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("2. Environment", styles["Heading2"]))
    story.append(
        Paragraph(
            "Remote host: <font name='Courier'>ubuntu@192.168.40.128</font><br/>"
            "Remote OS: Ubuntu 20.04.6 LTS<br/>"
            "ROS version: ROS Noetic 1.17.4<br/>"
            "Local machine: Windows host on VMware NAT network<br/>"
            "Simulation model: <font name='Courier'>TURTLEBOT3_MODEL=waffle</font>",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("3. Part 2: TurtleBot3 Gazebo and RViz", styles["Heading2"]))
    story.append(
        Paragraph(
            "The TurtleBot3 <font name='Courier'>waffle</font> model was used because it provides both camera and "
            "LiDAR sensors. The simulation topics <font name='Courier'>/scan</font> and "
            "<font name='Courier'>/camera/rgb/image_raw</font> were verified successfully, and RViz was configured "
            "to display LaserScan data together with the image panel.",
            styles["BodySmall"],
        )
    )
    story.append(
        Preformatted(
            "source /opt/ros/noetic/setup.bash\n"
            "export TURTLEBOT3_MODEL=waffle\n"
            "roslaunch turtlebot3_gazebo turtlebot3_world.launch\n"
            "roslaunch turtlebot3_bringup turtlebot3_remote.launch\n"
            "roslaunch turtlebot3_gazebo turtlebot3_simulation.launch\n"
            "rviz -d /home/ubuntu/lab4_turtlebot3_image.rviz",
            styles["CodeBlock"],
        )
    )
    story.append(fit_image(GENERATED / "part2_manual_screenshot.png", 16.8, 10.6))
    story.append(
        Paragraph(
            "Figure 1. Final RViz/Gazebo screenshot for Part 2. The RViz window shows the image panel and "
            "LaserScan result while the Gazebo window confirms the TurtleBot3 simulation world.",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("4. Part 3: Multi-Computer Interaction", styles["Heading2"]))
    story.append(
        Paragraph(
            "The remote Ubuntu machine kept the TurtleBot3 robot side running, while the local Windows machine "
            "published keyboard teleoperation commands to the remote ROS system. In this workstation setup, "
            "<font name='Courier'>rosbridge_server</font> and a local Python teleop client were used to realize "
            "the local-to-remote control path.",
            styles["BodySmall"],
        )
    )
    story.append(
        Preformatted(
            "# Remote Ubuntu\n"
            "source /opt/ros/noetic/setup.bash\n"
            "roslaunch turtlebot3_gazebo turtlebot3_world.launch\n"
            "roslaunch turtlebot3_bringup turtlebot3_remote.launch\n"
            "roslaunch rosbridge_server rosbridge_websocket.launch\n\n"
            "# Local Windows\n"
            "python tmp\\rosbridge_keyboard_teleop.py --host 192.168.40.128",
            styles["CodeBlock"],
        )
    )
    story.append(
        Paragraph(
            "During verification, the local teleop client successfully published forward, turn-left, and stop "
            "commands. The remote machine reported active nodes such as "
            "<font name='Courier'>/robot_state_publisher</font>, <font name='Courier'>/rosbridge_websocket</font>, "
            "and the expected topics <font name='Courier'>/cmd_vel</font>, <font name='Courier'>/scan</font>, "
            "and <font name='Courier'>/camera/rgb/image_raw</font>.",
            styles["BodySmall"],
        )
    )
    story.append(fit_image(GENERATED / "part3_remote_manual.png", 15.5, 9.0))
    story.append(
        Paragraph(
            "Figure 2. Remote-machine screenshot for Part 3, showing the ROS nodes and key topics on the Ubuntu side.",
            styles["BodySmall"],
        )
    )
    story.append(fit_image(GENERATED / "part3_local_manual.png", 15.5, 8.5))
    story.append(
        Paragraph(
            "Figure 3. Local-machine screenshot for Part 3, showing the keyboard teleoperation client running on Windows.",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("5. Part 4: Camera Calibration", styles["Heading2"]))
    story.append(
        Paragraph(
            "No physical USB camera device was attached to the VMware Ubuntu machine during this session. "
            "Therefore, a synthetic monocular chessboard stream was used to complete the calibration demonstration. "
            "This still demonstrates the calibration principle correctly: chessboard corners were detected from "
            "multiple views, and intrinsic and distortion parameters were solved and written into a YAML file.",
            styles["BodySmall"],
        )
    )
    story.append(
        Paragraph(
            "Final calibration results:<br/>"
            "camera_matrix = [633.279533, 0.0, 317.464722; 0.0, 628.144225, 238.798925; 0.0, 0.0, 1.0]<br/>"
            "distortion_coefficients = [0.033008, -0.340623, 0.000056, -0.001492, 1.192364]<br/>"
            "reprojection_error = 0.065537<br/>"
            "valid_views = 16",
            styles["BodySmall"],
        )
    )
    story.append(fit_image(GENERATED / "part4_calibration_corners.png", 12.5, 8.5))
    story.append(
        Paragraph(
            "Figure 4. Corner-detection result from the calibration dataset.",
            styles["BodySmall"],
        )
    )
    story.append(fit_image(GENERATED / "part4_camera_parameters.png", 16.5, 8.5))
    story.append(
        Paragraph(
            "Figure 5. Final camera parameter file used as the Part 4 submission screenshot.",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("6. Conclusion", styles["Heading2"]))
    story.append(
        Paragraph(
            "Lab 4 was completed with verified TurtleBot3 simulation, validated multi-computer control, and a completed "
            "camera calibration parameter set. The final screenshots for Part 2 and Part 3 were manually captured and "
            "included in this report, while the Part 4 calibration result was generated from a synthetic dataset because "
            "no physical camera was attached to the virtual machine.",
            styles["BodySmall"],
        )
    )

    doc.build(story)
    print(OUT_PDF)


if __name__ == "__main__":
    build_pdf()
