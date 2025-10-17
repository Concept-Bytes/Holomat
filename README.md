# HoloMat Framework

A powerful, extensible framework for creating interactive projection-based applications using hand tracking. Transform any surface into an interactive display with this easy-to-use system.

![HoloMat Demo](https://via.placeholder.com/800x400.png?text=HoloMat+Demo)

## 🚀 Features

- **Hand Tracking**: Accurate hand landmark detection using MediaPipe
- **Projection Mapping**: Seamless camera-to-projector calibration
- **Modular App System**: Easily create and manage multiple applications
- **Touchless Interaction**: Intuitive hand gesture controls
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/cklam12345/holomat.git
   cd holomat
   ```

> ℹ️ **Note**: This project was forked from [Concept-Bytes/Holomat](https://github.com/Concept-Bytes/Holomat). Special thanks to Concept Bytes for creating this innovative framework.

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Additional dependencies for specific apps:
   ```bash
   # For depth estimation app
   pip install torch torchvision
   pip install transformers
   ```

## 🎮 Quick Start

### 1. First-Time Setup

1. **Calibrate Your Setup**:
   ```bash
   python hand_calibartion.py
   ```
   - Follow the on-screen instructions to calibrate the four corners
   - This creates `M.npy` with the transformation matrix

2. **Test the Calibration**:
   ```bash
   python run.py
   ```
   - Move your hand in front of the camera
   - You should see green dots tracking your hand movements

### 2. Launch the Home Screen
```bash
python home_screen.py
```
- Navigate the interface using hand gestures
- Hover over apps to select them
- Use the center home button to return to the main menu

## 📱 Available Apps

1. **Measurement Tool** (`app_1`)
   - Measure distances between points with pinch gestures
   - Visual feedback with real-time measurements

2. **Depth Estimation** (`app_2`)
   - Create depth maps using AI
   - Save and analyze depth information

3. **Your App Here**
   - The framework makes it easy to add your own applications!

## 🛠 Creating Your Own App

1. **Create a new app directory**:
   ```
   mkdir apps/app_X
   ```

2. **Add your app files**:
   - `app_X.py`: Your main application code
   - `app_X.jpg`: App icon (200x200px recommended)

3. **Basic app template** (`app_X.py`):
   ```python
   import pygame
   
   def run(screen, camera_manager):
       """
       Main function for your app
       
       Args:
           screen: Pygame display surface
           camera_manager: Handles camera and tracking
       """
       running = True
       clock = pygame.time.Clock()
       
       while running:
           # Handle events
           for event in pygame.event.get():
               if event.type == pygame.QUIT:
                   running = False
           
           # Get hand landmarks
           landmarks = camera_manager.get_transformed_landmarks()
           
           # Your app logic here
           screen.fill((0, 0, 0))  # Clear screen
           
           # Draw something
           if landmarks:
               # Example: Draw first landmark
               x, y = int(landmarks[0][0][0]), int(landmarks[0][0][1])
               pygame.draw.circle(screen, (0, 255, 0), (x, y), 10)
           
           pygame.display.flip()
           clock.tick(60)
       
       return  # Returns to home screen
   ```

## 🌟 Tips for Best Results

- Ensure good lighting for accurate hand tracking
- Position the camera to have a clear view of the projection surface
- Recalibrate if you move the camera or projector
- Keep your hand within the camera's field of view

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgments

This project is built on the belief that sharing knowledge and collaboration can create a better future. Special thanks to:

- [Concept Bytes](https://github.com/Concept-Bytes) for creating and open-sourcing the original Holomat project
- [MediaPipe](https://mediapipe.dev/) for their incredible hand tracking technology
- [OpenCV](https://opencv.org/) for their powerful computer vision tools
- [Pygame](https://www.pygame.org/) for making rendering accessible
- The entire open-source community that makes projects like this possible

Together, through open collaboration, we can build tools that push the boundaries of interactive technology and create meaningful change.

---

💡 **Pro Tip**: Check out the `sample.env` file to customize screen resolution and other settings!
