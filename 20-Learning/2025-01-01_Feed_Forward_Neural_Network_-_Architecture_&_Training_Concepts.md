---
certification: ''
confidence: high
date: '2025-01-01'
keywords:
- weights
- biases
- activation function
- epoch
- batch
- loss function
- classification
- regression
- hidden layer
- prediction
project: ''
status: to-review
tags:
- neural-network
- deep-learning
- feedforward
- backpropagation
- training
target_folder: 20-Learning
technology: gen-ai
title: Feed Forward Neural Network - Architecture & Training Concepts
type: lesson-learned
---

Feed Forward neural network

Input
w1  b1  w2  b2
hidden layer1  hidden layer2  output layer

Input1 O
Input2 O
Input3 O

O Output1
O Output2

Prediction { Classification
             Regression

w: Weight
b: biases
a: activation function

Epoch  1  2  3  4  5  6  7n  8
       [batch diagram] --> N

N: Training size = N
n: Batch size = n        N = n × S
S: Number of steps = S

Loss function: L

           Prediction        Target
           ŷ    ←loss→    y
                function

           * lower is better
             than higher

![Feed Forward Neural Network Diagram](../assets/2026-06-30-diagram-01.png)
> **Auto description:** A hand-drawn neural network diagram with three layers connected by green arrows. The leftmost layer (Input) contains 3 nodes labeled Input1, Input2, Input3. The middle section shows two hidden layers (hidden layer1 and hidden layer2), each with 4 nodes arranged vertically. The rightmost layer (output layer) contains 2 nodes labeled Output1 and Output2. Green arrows connect every node in each layer to every node in the next layer (fully connected). Labels w1, b1 appear above the first hidden layer and w2, b2 above the second hidden layer.

![Epoch / Batch Training Timeline Diagram](../assets/2026-06-30-diagram-02.png)
> **Auto description:** A horizontal bar diagram representing training epochs and batches. The bar is divided into numbered segments (1, 2, 3, 4, 5, 6, 7n, 8) representing steps or batches within an epoch. The bar ends with a large arrow pointing right toward 'N', indicating the total training size. Small dots and marks inside the bar represent individual data batches.

![Loss Function Flow Diagram](../assets/2026-06-30-diagram-03.png)
> **Auto description:** A simple flow diagram showing the relationship between Prediction (ŷ) and Target (y) through a loss function. An arrow labeled 'loss function' connects ŷ on the left to y on the right, illustrating how the loss is computed between the predicted and target values.
