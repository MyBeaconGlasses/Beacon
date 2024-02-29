<a name="mybeacon"></a> 

# MyBeacon

[Web Demo Link](https://www.mybeacon.tech/)

[Demo Video Link](https://youtu.be/VnC7osXl1UQ)


<a name="overview"></a>

## Overview

MyBeacon delivers smart glasses, an affordable device designed with accessibility at its core. By integrating eye tracking, cameras, and real-time voice transcriptions, we offer a seamless and intuitive experience that ensures that everyone, regardless of their physical capabilities, can interact with technology effortlessly.

<a name="contributors"></a>

## Contributors
1. [Bill Zhang](mailto:billzhangsc@gmail.com)
2. [Elissa Yang](mailto:eyang.zeta@gmail.com)
3. [Simon Quach](mailto:simonquach.tech@gmail.com)
4. [Audrey Chen](mailto:audgeviolin07@gmail.com)

<a name="table-of-contents"></a>

## Table of Contents
- [MyBeacon](#mybeacon)
    - [Overview](#overview)
    - [Contributors](#contributors)
    - [Table of Contents](#table-of-contents)
    - [Inspiration](#inspiration)
    - [Goals](#goals)
    - [Built With](#built-with)
        - [Software](#software)
        - [Hardware](#hardware)
    - [Challenges](#challenges)
    - [Accomplishments](#accomplishments)
    - [What we Learned](#what-we-learned)
    - [What's Next](#whats-next)
    - [How to run](#how-to-run)

<a name="inspiration"></a>

## Inspiration

Our project sprang from a simple idea: to make technology accessible to everyone, especially those challenged by physical and sensory limitations. Traditional tech interfaces like keyboards and screens often put these individuals at a disadvantage. 
 Our mission is to design solutions that overcome these obstacles, ensuring that technology is inclusive and accessible to everyone, regardless of their physical abilities.

<a name="goals"></a>

## Goals
- Provide real-time information on the go as requested by the user through voice command
- Enhance accessibility to technology for individuals facing physical, sensory, and technological challenges
- Allow people to navigate language barriers
- Be seamlessly compatible with new features and capabilities

<a name="built-with"></a>

## Built With

<a name="software"></a>

### Software
- "Mixture of experts" system using multiple specialized LLMs.
- Web Demo frontend UI built with Next.js and Tailwind CSS.
- FastAPI handles concurrent connections for backend services.
- Websockets enable two-way communication between device and server.

<a name="hardware"></a>

### Hardware
- Raspberry Pi 4B as our microcontroller of choice.
- Adafruit Camera 3 Wide captures user's field of view for image segmentation.
- User voice command input received through Adafruit USB Microphone.
- Responses played through SunFounder Raspberry Pi Speaker and Amplifier Modules.

<a name="challenges"></a>

## Challenges
- Implementing AI image segmentation on the glasses due to imited documentation
- Acquiring PCBs in a timely manner due to shipping limitations

<a name="accomplishments"></a>

## Accomplishments
1. Our team successfully implemented a wearable AI voice assistant, complete with eye tracking and image segmentation.
2. Our smart glasses offer an intuitive experience using  voice-activated controls and audio feedback.
3. The voice assistant is powered by a mixture of experts working together to provide users with essential functions.
4. The hardware is assembled from parts and materials selected with both performance and affordability in mind.
5. MyBeacon smart glasses are designed with future expansion in mind, ensuring that new features can be seamlessly integrated.

<a name="what-we-learned"></a>

## What We learned

Throughout the development of MyBeacon smart glasses, our team learned:

- The challenges of implementing complex programs while keeping hardware limitations in mind
- The value of user feedback at every prototyping stage
- The importance of designing PCBs and 3D models with precise matching measurements 

<a name="whats-next"></a>

## What's Next
- Implement more experts, broadening the range of functions offered.
- Conduct more trials with people who stand to benefit the most from MyBeacon, such as immigrants and individuals with limited mobility and/or sight.

<a name="how-to-run"></a>

## How to run

1. Clone the repository
2. Run Frontend
    1. `cd website`
    2. `npm install`
    3. `npm start`

3. Run Backend
    1. `cd server`
    2. `npm install`
    3. `npm start`

Some backend links and environmental variables will be required; please contact us for more information.
