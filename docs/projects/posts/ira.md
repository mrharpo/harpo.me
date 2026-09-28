---
title: 'Ira - Interactive, Reactive, Autonomous LEDs'
date: 2021-07-20
tags:
  - tech
---
Realtime LED pixel controll with Ira

![ Realtime LED pixel controll ](../../assets/ira.gif)
<!-- more -->

### Ira - an **Interactive**, **Reactive**, **Autonomous** LED Controller

**Ira** is an open-source, real-time microcontroller library for individually addressable LED lights, such as the WS2811 (and …12, …13, etc), and others.

Originally designed for theatrical applications, I’ve used it as home decorations, Halloween lights, 3D printer status, and even on my Christmas tree!

### Any Light, Any Color, Any Time!

With modern, individually addressable LED lights, some control architecture is needed to tell each light what color to be.

Even with excellent libraries like [FastLED](https://github.com/FastLED/FastLED), it only handles signaling the lights. It does not decide what effects to run. That is all left to the user to implement.

And if you want to run special effects, you need some way of telling the controller what state for the effects to be in, and possibly providing some parameters, like:

- What color should it be?
- How fast show the effect go?
- Should it run forwards or backwards?
- Should the colors shift, and how fast?

Theses are just a few examples of variable parameters that can be controlled dynamically in any moment.

### Reliability

![ One Arduino to controll the lights, another to listen the DMX signal ](../../assets/ira-circuit.jpg) One Arduino to controll the lights, another to listen the DMX signal

For home applications, a simple python script running a web server is enough to control the application from a phone over a wifi network. Any reliability issues can be dealt with by resending a message.

In the case of theatrical applications, something more robust like DMX needs to be used. To offload the burden of decoding the DMX signal, a separate receiver module acts as dedicated listener to allow the full processing power of the microcontroller to handle the LED effects.

### Timing

Special care also has to be made in writing the effects, since there’s no guarantee of how long it might take for a small controller to do all the maths to determine the color for each pixel at a reasonable frame rate.

If it takes 100 microseconds to generate the color for a pixel, a small installation of 100 lights could have a refresh rate in the 100Hz range. But when controlling 1000 lights, that drops down to 10 Hz - very choppy movement to the eye.

### Availability

Beyond ensuring each frame of effect is rendered timely, every function needs to be able to “pause” frequently and allow the controller to listen for further instructions. After each frame is generated and sent, the controller checks for new instructions, and activates the appropriate effect.

More information available at [quaternion.media/ira](https://quaternion.media/ira)

All details and code [available on github!](https://github.com/quaternionmedia/ira)
